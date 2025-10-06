package com.example.batchprocessing;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;

@RestController
@RequestMapping("/api")
public class JobController {

    private final JobLauncher jobLauncher;
    private final Job job;

    @Autowired
    public JobController(JobLauncher jobLauncher, Job job) {
        this.jobLauncher = jobLauncher;
        this.job = job;
    }

    @PostMapping("/run-job")
    public String runJob() {
        try {
            JobParameters params = new JobParametersBuilder()
                    .addLong("timestamp", Instant.now().toEpochMilli()) // уникальный параметр
                    .toJobParameters();

            jobLauncher.run(job, params);
            return "Job started successfully at " + Instant.now();
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to start job: " + e.getMessage();
        }
    }
}
