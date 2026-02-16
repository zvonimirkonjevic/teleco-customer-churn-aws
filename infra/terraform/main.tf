data "aws_sagemaker_prebuilt_ecr_image" "xgboost" {
  region = var.default_region
  repository_name = "xgboost"
  image_tag = "latest"
}