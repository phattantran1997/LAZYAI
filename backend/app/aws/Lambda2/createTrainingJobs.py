import boto3
import os
import time

def lambda_handler(event, context):
    """AWS Lambda handler for creating SageMaker training jobs."""
    try:
        sagemaker = boto3.client("sagemaker")
        job_name = f"finetune-llama3-{int(time.time())}"
        
        # Get role ARN from environment variables
        role_arn = os.environ.get("SAGEMAKER_ROLE_ARN")
        if not role_arn:
            raise ValueError("SAGEMAKER_ROLE_ARN environment variable is required")
        
        # Get configuration from environment variables or use defaults
        training_image = os.environ.get("SAGEMAKER_TRAINING_IMAGE", "your-custom-image-uri")
        output_s3 = os.environ.get("SAGEMAKER_OUTPUT_S3", "s3://your-sagemaker-output-bucket/finetuned-model/")
        input_s3 = os.environ.get("SAGEMAKER_INPUT_S3", "s3://lazyai-output-chunkdata/")
        
        # Get hyperparameters from event or use defaults
        hyperparameters = event.get("hyperparameters", {
            "epochs": "3",
            "learning_rate": "2e-4",
            "batch_size": "2"
        })

        response = sagemaker.create_training_job(
            TrainingJobName=job_name,
            AlgorithmSpecification={
                "TrainingImage": training_image,
                "TrainingInputMode": "File"
            },
            RoleArn=role_arn,
            InputDataConfig=[
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": input_s3,
                            "S3DataDistributionType": "FullyReplicated"
                        }
                    },
                    "ContentType": "application/pdf"
                }
            ],
            OutputDataConfig={
                "S3OutputPath": output_s3
            },
            ResourceConfig={
                "InstanceType": "ml.g4dn.xlarge",
                "InstanceCount": 1,
                "VolumeSizeInGB": 100
            },
            StoppingCondition={
                "MaxRuntimeInSeconds": 60 * 60 * 4  # 4 hours
            },
            HyperParameters=hyperparameters
        )
        
        print(f"✅ Started SageMaker training job: {job_name}")
        return {
            "statusCode": 200,
            "body": {
                "status": "started", 
                "job_name": job_name,
                "sagemaker_response": response
            }
        }
        
    except Exception as e:
        print(f"❌ Error creating SageMaker training job: {str(e)}")
        return {
            "statusCode": 500,
            "body": {
                "status": "error",
                "message": str(e)
            }
        }

def test_local():
    """Test function for local development."""
    print("=== LOCAL TESTING MODE ===")
    
    # Set test environment variables
    test_env_vars = {
        "SAGEMAKER_ROLE_ARN": "arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole-20231201T000000",
        "SAGEMAKER_TRAINING_IMAGE": "123456789012.dkr.ecr.us-east-1.amazonaws.com/lazyai-training:latest",
        "SAGEMAKER_OUTPUT_S3": "s3://lazyai-sagemaker-output/finetuned-model/",
        "SAGEMAKER_INPUT_S3": "s3://lazyai-output-chunkdata/"
    }
    
    # Set environment variables for testing
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    # Test event
    test_event = {
        "hyperparameters": {
            "epochs": "3",
            "learning_rate": "2e-4",
            "batch_size": "2",
            "max_steps": "60"
        }
    }
    
    print("Environment variables set:")
    for key, value in test_env_vars.items():
        print(f"  {key}: {value}")
    
    print(f"\nTest event: {test_event}")
    
    # Test AWS credentials
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"\n✅ AWS credentials valid. Account: {identity['Account']}")
    except Exception as e:
        print(f"\n❌ AWS credentials error: {str(e)}")
        print("Please configure AWS credentials using:")
        print("  aws configure")
        print("  or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY environment variables")
        return
    
    # Run the lambda handler
    print("\n🚀 Testing lambda_handler...")
    result = lambda_handler(test_event, None)
    
    print(f"\nResult: {result}")

if __name__ == "__main__":
    # Run local testing
    test_local()
