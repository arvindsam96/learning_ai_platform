# CloudFront CDN
resource "aws_cloudfront_distribution" "app" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix} CloudFront Distribution"
  default_root_object = ""

  # Origin for the ALB
  origin {
    domain_name = aws_lb.app.dns_name
    origin_id   = "ALB-${aws_lb.app.name}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # Origin for S3 static assets (if needed)
  origin {
    domain_name = aws_s3_bucket.app_storage.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.app_storage.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.app.cloudfront_access_identity_path
    }
  }

  # Default behavior - route to ALB
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${aws_lb.app.name}"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0

    # Use CloudFront Functions for API routing (optional)
    # lambda_function_association {
    #   event_type   = "viewer-request"
    #   lambda_arn   = aws_lambda_function.api_router.qualified_arn
    #   include_body = false
    # }
  }

  # Cache behavior for static assets from S3
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.app_storage.bucket}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400  # 1 day
    max_ttl                = 31536000 # 1 year

    compress = true
  }

  # Custom error pages
  custom_error_response {
    error_code         = 500
    response_code      = 500
    response_page_path = "/500.html"
    error_caching_min_ttl = 300
  }

  custom_error_response {
    error_code         = 502
    response_code      = 502
    response_page_path = "/502.html"
    error_caching_min_ttl = 300
  }

  custom_error_response {
    error_code         = 503
    response_code      = 503
    response_page_path = "/503.html"
    error_caching_min_ttl = 300
  }

  custom_error_response {
    error_code         = 504
    response_code      = 504
    response_page_path = "/504.html"
    error_caching_min_ttl = 300
  }

  # SSL/TLS configuration
  viewer_certificate {
    cloudfront_default_certificate = true
    # For production, use ACM certificate:
    # acm_certificate_arn = aws_acm_certificate.app.arn
    # ssl_support_method  = "sni-only"
  }

  # Geo restrictions (optional)
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # WAF integration (optional)
  # web_acl_id = aws_wafv2_web_acl.app.arn

  tags = local.common_tags
}

# CloudFront Origin Access Identity for S3
resource "aws_cloudfront_origin_access_identity" "app" {
  comment = "${local.name_prefix} CloudFront OAI"
}

# Update S3 bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "app_storage_cloudfront" {
  bucket = aws_s3_bucket.app_storage.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontAccess"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.app.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.app_storage.arn}/*"
      }
    ]
  })
}
