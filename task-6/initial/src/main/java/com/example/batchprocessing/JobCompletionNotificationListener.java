package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Gauge;
import io.prometheus.client.Counter;
import io.prometheus.client.exporter.PushGateway;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.time.ZoneOffset;

@Component
public class JobCompletionNotificationListener implements JobExecutionListener {


private static final Logger log = LoggerFactory.getLogger(JobCompletionNotificationListener.class);
private final JdbcTemplate jdbcTemplate;

public JobCompletionNotificationListener(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
}

@Override
public void afterJob(JobExecution jobExecution) {
    log.info("Job finished with status: {}", jobExecution.getStatus());

    CollectorRegistry registry = new CollectorRegistry();

    Gauge totalProcessedGauge = Gauge.build()
            .name("spring_batch_processed_total")
            .help("Total number of products processed by Spring Batch job")
            .register(registry);

    Gauge jobDurationGauge = Gauge.build()
            .name("spring_batch_job_duration_seconds")
            .help("Job execution duration in seconds")
            .register(registry);

    Counter successCounter = Counter.build()
            .name("spring_batch_job_success_total")
            .help("Total number of successfully completed jobs")
            .register(registry);

    Counter failureCounter = Counter.build()
            .name("spring_batch_job_failure_total")
            .help("Total number of failed jobs")
            .register(registry);

    try {
        Map<String, String> groupingKey = new HashMap<>();
        groupingKey.put("job", "importProductJob");

        // Вычисляем длительность
        long duration = 0L;
        if (jobExecution.getStartTime() != null && jobExecution.getEndTime() != null) {
            duration = Duration.between(
            jobExecution.getStartTime().toInstant(ZoneOffset.UTC),
            jobExecution.getEndTime().toInstant(ZoneOffset.UTC)
            ).toSeconds();
        }
        jobDurationGauge.set(duration);

        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            Integer total = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM products", Integer.class);
            totalProcessedGauge.set(total);
            successCounter.inc();

            groupingKey.put("status", "COMPLETED");
            log.info("Job completed successfully. Duration: {}s, Total: {}", duration, total);
        } else {
            failureCounter.inc();
            groupingKey.put("status", jobExecution.getStatus().toString());
            log.warn("Job failed or stopped. Duration: {}s", duration);
        }

        // Отправляем все метрики
        PushGateway pg = new PushGateway("pushgateway:9091");
        pg.pushAdd(registry, "spring_batch_job", groupingKey);

        log.info("Metrics successfully pushed to PushGateway at pushgateway:9091");

    } catch (Exception e) {
        log.error("Failed to push metrics to PushGateway", e);
    }
}
}
