import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function that serializes target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        # decode to str for JSON
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Pass the data back to the Step Function
    print("Event keys:", event.keys())
    return {
        "image_data": image_data,
        "s3_bucket": bucket,
        "s3_key": key,
        "inferences": []
    }




import boto3
import base64
import json

runtime = boto3.client('sagemaker-runtime')

ENDPOINT = "image-classification-2025-09-06-20-04-11-218"

def lambda_handler(event, context):
    """A function that classifies the image data"""

    print("DEBUG incoming event:", json.dumps(event))
    image = base64.b64decode(event["image_data"])
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="image/png",
        Body=image
    )
    inferences = json.loads(response['Body'].read().decode('utf-8'))
    event["inferences"] = inferences
    return {
        "image_data": event["image_data"],
        "s3_bucket": event["s3_bucket"],
        "s3_key": event["s3_key"],
        "inferences": inferences
    }




import json

THRESHOLD = 0.93

def lambda_handler(event, context):
    """A function that checks if confidence threshold is met for the inference"""
    
    # Grab the inferences from the event
    inferences = event["inferences"]
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) >= THRESHOLD
    
    # If our threshold is met, pass our data back out of the Step Function
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    return event
