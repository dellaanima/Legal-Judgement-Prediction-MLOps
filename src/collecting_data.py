import subprocess

# Required packages
required_packages = ["pandas", "tqdm", "boto3"]

# Install packages function
def install_packages(package_list):
    for package in package_list:
        try:
            subprocess.check_call(["pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install package {package}: {e}")
            raise

# Fetch XML case list from URL
def fetch_case_list(url):
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
    response = urlopen(url).read()
    xtree = ET.fromstring(response)
    totalCnt = int(xtree.find('totalCnt').text)

    rows = []
    for page in trange(1, totalCnt // 20 + 1):
        page_url = f"{url}&page={page}"
        response = urlopen(page_url).read()
        xtree = ET.fromstring(response)

        try:
            items = xtree[5:]
        except:
            break

        for node in items:
            판례일련번호 = node.find('판례일련번호').text
            rows.append({'판례일련번호': 판례일련번호})

        if len(rows) >= 10:
            break
    case_list = pd.DataFrame(rows)
    return case_list


# Preprocessing Function 
def preprocess_laws_service(row):
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
    # '[n]'와 같은 형태의 숫자와 대괄호를 제거
    row = re.sub(r'\[\d+\]', '', row)

    # '제n항', '제n호', '단서 제n호'와 같은 부분을 제거
    row = re.sub(r'(제\d+항)|(제\d+호)|(단서 제\d+호)', '', row)

    # '/' 를 기준으로 법령을 분리하고, 각 법령에서 특수 기호를 제거
    laws = row.split('/')
    cleaned_laws = []
    for law in laws:
        cleaned_law = re.sub(r'[^\w\s]', '', law).strip()
        cleaned_laws.append(cleaned_law)

    # 최종적으로 '/'로 구분된 법령을 다시 합치기
    result = ' / '.join(cleaned_laws)

    return result



def fetch_case_data(case_id, base_url):
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
   # S3 bucket configuration
    s3_bucket = "sagemaker-us-east-1-353411055907"
    s3_client = boto3.client('s3')

    url = f"{base_url}{case_id}&type=XML&mobileYn="
    response = urlopen(url).read()
    xtree = ET.fromstring(response)

    case_data = {'판례일련번호': case_id}
    contents = ['참조조문', '판례내용']

    def remove_tag(content):
        if content is None:
            return ''
        cleaned_text = re.sub('<.*?>', '', content)
        return cleaned_text

    for content in contents:
        content_element = xtree.find(content)
        if content_element is not None:
            text = content_element.text
            text = remove_tag(text)

            if content == '판례내용':
                text = text[:250]
        else:
            text = ''

        if content == '참조조문':
            text = preprocess_laws_service(text)  

        case_data[content] = text
    return case_data



# Fetch existing case IDs data from S3
def fetch_existing_case_ids(bucket, key):
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
       # S3 bucket configuration
    s3_bucket = "sagemaker-us-east-1-353411055907"
    s3_client = boto3.client('s3')

    try:
        existing_data_obj = s3_client.get_object(Bucket=bucket, Key=key)
        existing_data = existing_data_obj['Body'].read().decode('utf-8')
        existing_case_ids = existing_data.strip().split('\n')
        return existing_case_ids
    except Exception as e:
        print(f"Error fetching existing case IDs: {e}")
        return []

# Filter new case IDs from the case list
def filter_new_case_ids(case_list, existing_case_ids):
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO

    new_case_ids = [case_id for case_id in case_list['판례일련번호'] if case_id not in existing_case_ids]
    new_case_list = case_list[case_list['판례일련번호'].isin(new_case_ids)]
    return new_case_list

# Update and store existing data
def update_existing_case_ids(new_case_list, existing_case_ids, bucket, key):

    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
       # S3 bucket configuration
    s3_bucket = "sagemaker-us-east-1-353411055907"
    s3_client = boto3.client('s3')

    updated_case_ids = existing_case_ids + new_case_list['판례일련번호'].tolist()
    updated_case_ids_str = '\n'.join(updated_case_ids)
    s3_client.put_object(Bucket=bucket, Key=key, Body=updated_case_ids_str.encode('utf-8'))

# Fetch and process case data
def process_case_data(new_case_list, existing_case_ids, bucket, existing_key, collected_data_key):
    
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
       # S3 bucket configuration
    s3_bucket = "sagemaker-us-east-1-353411055907"
    s3_client = boto3.client('s3')
    existing_case_ids = fetch_existing_case_ids(bucket, existing_key)
    if not existing_case_ids:
        print("No existing case IDs found.")
    else:
        print(f"Found {len(existing_case_ids)} existing case IDs.")

    base_url = "https://www.law.go.kr/DRF/lawService.do?OC=rnqhgml12&target=prec&ID="
    case_data_list = []

    for case_id in new_case_list['판례일련번호']:
        case_data = fetch_case_data(case_id, base_url)
        case_data_list.append(case_data)

    case_data_df = pd.DataFrame(case_data_list)
    update_existing_case_ids(new_case_list, existing_case_ids, bucket, existing_key)

    # Store added data in S3 as BytesIO
    file_content = case_data_df.to_csv(index=False).encode('utf-8')
    s3_client.put_object(Bucket=bucket, Key=collected_data_key, Body=BytesIO(file_content))

    # S3에서 labels.csv 가져오기
    labels_obj = s3_client.get_object(Bucket=bucket, Key='GP-LJP-mlops/data/labels.csv')
    labels_data = labels_obj['Body'].read().decode('cp949')
    labels_df = pd.read_csv(StringIO(labels_data))

    # laws_serivce 에서 row 만 포함하는 것만 선택 
    # Compare and filter the rows
    filtered_df = case_data_df[case_data_df['참조조문'].str.contains('|'.join(labels_df['laws_service']))]

    # Function to find matched 'laws_service' and 'laws_service_id'
    def find_matched_laws_service_id(row):
        matched_laws_service = [law for law in labels_df['laws_service'] if law in row['참조조문']]
        matched_laws_service_id = [str(labels_df.loc[labels_df['laws_service'] == law, 'laws_service_id'].values[0]) for law in matched_laws_service]
        return '|'.join(matched_laws_service_id)


    # Apply the function to create the 'matched_laws_service_id' column
    filtered_df['matched_laws_service_id'] = filtered_df.apply(find_matched_laws_service_id, axis=1)

    # Concatenate matched 'laws_service' values in 'filtered_df'
    filtered_df['matched_laws_service'] = filtered_df.apply(lambda row: '|'.join([law for law in labels_df['laws_service'] if law in row['참조조문']]), axis=1)

    # Extract the specified columns and rename them
    final_df = filtered_df[['matched_laws_service_id', '판례내용', 'matched_laws_service']].copy()

    final_df.rename(columns={'matched_laws_service_id': 'laws_service_id', '판례내용' : 'fact', 'matched_laws_service': 'laws_service'}, inplace=True)



    final_df = final_df[~final_df['laws_service_id'].str.contains(r'\D')] 
   
    file_name = 'GP-LJP-mlops/data/collected_data/final_data.csv' 
    obj = s3.get_object(Bucket=bucket, Key=file_name)
    existing_data = pd.read_csv(obj['Body'])


    # combine
    combined_data = pd.concat([existing_data, added_df], axis=0)
    # drop na 
    combined_data = combined_data.dropna(axis=1, how='all')
    # to csv
    combined_csv = combined_data.to_csv(index=False)

    # upload
    s3.put_object(Bucket=bucket, Key=file_name, Body=combined_csv)  



# Main execution function
def main():
    install_packages(required_packages)
    
    import pandas as pd
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re
    import boto3
    from io import BytesIO
    from tqdm import trange
    from io import StringIO
    
    # S3 bucket configuration
    s3_bucket = "sagemaker-us-east-1-353411055907"
    s3_client = boto3.client('s3')
    
    existing_key = 'GP-LJP-mlops/data/collected_data/existing_case_ids.csv'
    collected_data_key = 'GP-LJP-mlops/data/collected_data/collected_data.csv'

    case_list_url = "https://www.law.go.kr/DRF/lawSearch.do?OC=rnqhgml12&target=prec&type=XML"
    case_list = fetch_case_list(case_list_url)

    existing_case_ids = fetch_existing_case_ids(s3_bucket, existing_key)
    new_case_list = filter_new_case_ids(case_list, existing_case_ids)

    if not new_case_list.empty:
        process_case_data(new_case_list, existing_case_ids, s3_bucket, existing_key, collected_data_key)
        print("Data collection and storage completed.")
    else:
        print("No new case IDs found. Nothing to update.")

if __name__ == "__main__":
    main()
