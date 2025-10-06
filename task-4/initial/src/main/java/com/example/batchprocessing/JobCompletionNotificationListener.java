package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
public class JobCompletionNotificationListener implements JobExecutionListener {

    private static final Logger log = LoggerFactory.getLogger(JobCompletionNotificationListener.class);

    private final JdbcTemplate jdbcTemplate;

    public JobCompletionNotificationListener(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            log.info("!!! JOB FINISHED! Time to verify the results");

            String sql = "SELECT productId, productSku, productName, productAmount, productData FROM products";

            jdbcTemplate.query(sql, (rs, rowNum) -> new Product(
                rs.getLong("productId"),
                rs.getLong("productSku"),
                rs.getString("productName"),
                rs.getLong("productAmount"),
                rs.getString("productData")
            )).forEach(product -> log.info("Found <{}> in the database.", product));

            log.info("Total products processed: {}",
                jdbcTemplate.queryForObject("SELECT COUNT(*) FROM products", Integer.class));
        }
    }
}