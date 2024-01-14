import subprocess

# List of required packages
required_packages = [
    "torch==1.11.0", 
    "transformers",
    "datasets==1.18.4"
]

# Function to install required packages
def install_packages(package_list):
    try:
        subprocess.check_call(["pip", "install"] + package_list)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        raise

def main():
    # Install required packages
    install_packages(required_packages)
    import pandas as pd
    import boto3
    from io import BytesIO
    from datasets import load_dataset, Dataset
    from transformers import AutoTokenizer

    # Model and tokenizer information
    model_id = 'lawcompany/KLAID_LJP_base'
    dataset_name = 'lawcompany/KLAID'
    small_subset_for_debug = True
    train_dir = '/opt/ml/processing/train'
    test_dir = '/opt/ml/processing/test'
        
    # Data Crawling
    # Download tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Tokenization helper function
    def tokenize(batch):
        return tokenizer(batch['fact'], padding='max_length', max_length=512, truncation=True)

    # Load datasets 
    train_dataset, test_dataset = load_dataset(dataset_name, split=['train[:1500]', 'train[-1500:]'])

    # Convert train dataset to DataFrame
    train_df = pd.DataFrame(train_dataset)

    # S3 Configuration
    s3 = boto3.client("s3")
    s3_bucket = "sagemaker-us-east-1-353411055907"
    file_name = 'GP-LJP-mlops/data/collected_data/final_data.csv'
    local_file_path = "/opt/ml/processing/final_data.csv"  

    # Download collected data from S3 and convert to DataFrame
    s3.download_file(s3_bucket, file_name, local_file_path)
    with open(local_file_path, "rb") as file:
        file_content = file.read()
        file_buffer = BytesIO(file_content)
        added_df = pd.read_csv(file_buffer, encoding='utf-8', header=None)
    
    
    added_df.columns = ['laws_service_id', 'fact', 'laws_service']
    # Merge original and collected data
    merged_df = pd.concat([train_df, added_df], axis=0)
    # Convert merged DataFrame to Hugging Face Dataset format
    train_dataset = Dataset.from_pandas(merged_df)

    # Select a small subset for debugging
    if small_subset_for_debug:
        train_dataset = train_dataset.shuffle().select(range(1000))
        test_dataset = test_dataset.shuffle().select(range(1000))

    # Tokenize datasets
    train_dataset = train_dataset.map(tokenize, batched=True)
    test_dataset = test_dataset.map(tokenize, batched=True)

    # Set format for PyTorch
    train_dataset = train_dataset.rename_column("laws_service_id", "labels")
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
    test_dataset = test_dataset.rename_column("laws_service_id", "labels")
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
    
    # Save datasets to disk
    train_dataset.save_to_disk(train_dir)
    test_dataset.save_to_disk(test_dir)

if __name__ == "__main__":
    main()
