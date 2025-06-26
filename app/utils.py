from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated ="auto")

##helper to hash passwords
def hash(password: str):
    return pwd_context.hash(password)

## verify 
def verify(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

import boto3
from app.models.config import Settings
import io
settings = Settings() 
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException,status

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class S3Client:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self):
        if self._client is None:
            try:
                self._client = boto3.client(
                    "s3",
                    aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                ## Test connection
                self._client.head_bucket(Bucket = settings.S3_BUCKET)
                logger.info("S# client initialized successfuly")
            except NoCredentialsError:
                logger.error("No credentials found")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = "AWS credentials not configured"

                )
            except ClientError as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail= "Failed to connect to S3"
                )
        return self._client
    
s3_client_instance = S3Client()

def upload_file_to_s3(file_bytes, filename, content_type = "application/octet-stream"):
    logger.info("starting upload....")
    try: 
        s3 = s3_client_instance.get_client()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content is empty"
            )
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                                detail = "Filename is required"
            )
        
        """Upload file"""
        s3.upload_fileobj(
            Fileobj=io.BytesIO(file_bytes),
            Bucket = settings.S3_BUCKET,
            Key = filename,
            ExtraArgs={"ContentType": content_type}
        )
        logger.info(f"succesfully uploaded file: {filename}")
        return filename
    except ClientError as e:

        error_code = e.response['Error']['Code']
        logger.error(f"S3 upload failed for {filename}: {error_code} - {e}")

        if error_code == 'NoSuchBucket':      
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= "S3 bucket  not found"
            )
        elif error_code == 'AccessDenied':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= "Access denied tp s3 bucket"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= f"File upload failed: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "File upload failed due tp unexpected error"
        )
        
    

def generate_presigned_url(filename, expires_in=900):
    try:
        s3 = s3_client_instance.get_client()

        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "Filename is required"
            )
        
        
    
        try:
            s3.head_object(Bucket=settings.S3_BUCKET, Key=filename)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found in S3"
                )
            raise

        url = s3.generate_presigned_url(
            'get_object',
            Params = {'Bucket': settings.S3_BUCKET, 'Key': filename},
            ExpiresIn=expires_in
        )
        logger.info(f"Generated presigned URL for: {filename}")
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate file access URL"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate file access URL"
        )
    
def test_s3_connection():
    """
    Test S3 connection and permissions
    """
    try:
        s3 = s3_client_instance.get_client()
        
        # Test 1: Check if bucket exists and is accessible
        print("Testing S3 connection...")
        s3.head_bucket(Bucket=settings.S3_BUCKET)
        print("✅ Bucket exists and is accessible")
        
        # Test 2: Test upload permissions
        print("Testing upload permissions...")
        test_content = b"Test file content"
        test_filename = "test-connection.txt"
        
        s3.upload_fileobj(
            Fileobj=io.BytesIO(test_content),
            Bucket=settings.S3_BUCKET,
            Key=test_filename,
            ExtraArgs={"ContentType": "text/plain"}
        )
        print("✅ Upload successful")
        
        # Test 3: Test presigned URL generation
        print("Testing presigned URL generation...")
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET, 'Key': test_filename},
            ExpiresIn=300
        )
        print(f"✅ Presigned URL generated: {url[:50]}...")
        
        # Test 4: Test delete permissions
        print("Testing delete permissions...")
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=test_filename)
        print("✅ Delete successful")
        
        print("\n🎉 All S3 tests passed! Your setup is working correctly.")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("Check your .env file and AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{settings.S3_BUCKET}' does not exist")
            print("Create the bucket in AWS S3 console first")
        elif error_code == 'AccessDenied':
            print("❌ Access denied - check your IAM permissions")
            print("Your AWS user needs s3:GetObject, s3:PutObject, s3:DeleteObject, s3:ListBucket permissions")
        else:
            print(f"❌ AWS Error: {error_code} - {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Run this test when starting your app or in a separate script
if __name__ == "__main__":
    test_s3_connection()