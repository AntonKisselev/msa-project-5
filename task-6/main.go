package main

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	stdouttrace "go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
)

var (
	logger = logrus.New()
	tracer trace.Tracer
)

// initTracer инициализирует stdout exporter и tracer provider
func initTracer(ctx context.Context, serviceName string) (func(context.Context) error, error) {
	exp, err := stdouttrace.New(stdouttrace.WithPrettyPrint())
	if err != nil {
		return nil, err
	}

	res, err := resource.Merge(
		resource.Default(),
		resource.NewWithAttributes(
			"", // добавили schemaURL
			attribute.String("service.name", serviceName),
		),
	)
	if err != nil {
		return nil, err
	}

	bsp := sdktrace.NewBatchSpanProcessor(exp)
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithResource(res),
		sdktrace.WithSpanProcessor(bsp),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{})

	tracer = otel.Tracer("batch-client")

	return tp.Shutdown, nil

}

// runJob — выполняет HTTP POST с трейсингом и логированием
func runJob(ctx context.Context, client *http.Client, url string) error {
	ctx, span := tracer.Start(ctx, "runJob",
		trace.WithAttributes(attribute.String("http.target", url)),
	)
	defer span.End()

	start := time.Now()
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, nil)
	if err != nil {
		logger.WithError(err).Error("failed to create request")
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return err
	}

	resp, err := client.Do(req)
	duration := time.Since(start)

	sc := trace.SpanContextFromContext(ctx)
	traceID := sc.TraceID().String()
	spanID := sc.SpanID().String()

	fields := logrus.Fields{
		"traceId": traceID,
		"spanId":  spanID,
		"uri":     url,
		"method":  "POST",
		"latency": duration.String(),
	}

	if err != nil {
		logger.WithFields(fields).WithError(err).Error("request failed")
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
		return err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	fields["status"] = resp.StatusCode
	fields["response"] = string(body)

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		logger.WithFields(fields).Info("job started successfully")
		span.SetStatus(codes.Ok, "job started successfully")
	} else {
		logger.WithFields(fields).Warn("job start returned non-2xx")
		span.SetStatus(codes.Error, fmt.Sprintf("status=%d", resp.StatusCode))
	}

	return nil

}

func main() {
	target := os.Getenv("BATCH_API_URL")
	if target == "" {
		target = "http://localhost:8080/api/run-job"
	}
	serviceName := os.Getenv("OTEL_SERVICE_NAME")
	if serviceName == "" {
		serviceName = "batch-run-client"
	}

	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})

	ctx := context.Background()
	shutdown, err := initTracer(ctx, serviceName)
	if err != nil {
		logger.WithError(err).Fatal("failed to init tracer")
	}
	defer func() { _ = shutdown(ctx) }()

	httpClient := &http.Client{
		Transport: otelhttp.NewTransport(http.DefaultTransport),
		Timeout:   20 * time.Second,
	}

	if err := runJob(ctx, httpClient, target); err != nil {
		logger.WithError(err).Fatal("runJob failed")
	}

}
