# Legal Judgement Prediction MLOps Project
With the advancement of artificial intelligence, the use of technology in the legal field is on the rise, and Legal Tech is leading the way in applying technology to the legal domain.
However, Legal Tech services face challenges such as complex user interfaces, operational complexities of machine learning services, and performance degradation of machine learning models. In this project, we propose a MLOps-based judgment document retrieval service to address these issues. The MLOps-based judgment document retrieval service provides a user-friendly interface and employs the MLOps (Machine Learning Operations) methodology to address the operational complexities of machine learning services and performance degradation of machine learning models in the legal domain.

- In this project, a pretrained model from Hugging Face was used. The specific pretrained model utilized is the 'KLUE RoBERTa-base', which is a text classification model fine-tuned on KLAID (Korean Legal Artificial Intelligence Datasets). This model was further fine-tuned using data collected through the pipeline, representing a training approach that iteratively refines the model's performance. Data for this project was collected from the National Law Information Center API.(https://open.law.go.kr/LSO/main.do) Additionally, the ML pipeline for this project was executed within SageMaker Studio Lab.

## MLOps System Architecture
![image](https://github.com/dellaanima/Legal-Judgement-Prediction-MLOps/assets/82052850/5263b19d-c27d-49ba-87f7-105f11c448ec)

## ML Pipleine Execution Demo 
![녹화_2023_09_12_22_40_49_78](https://github.com/dellaanima/Legal-Judgement-Prediction-MLOps/assets/82052850/6fd14da1-c103-4880-a684-642fd52e7567)

## Legal Judgment Prediction Service Demo 
![녹화_2024_01_18_21_05_59_373(1)](https://github.com/dellaanima/Legal-Judgement-Prediction-MLOps/assets/82052850/23a882e2-91c7-46ff-9d8a-77ec52fee94f)



---
References: 

- https://github.com/gonsoomoon-ml/SageMaker-Pipelines-Step-By-Step
- https://github.com/gonsoomoon-ml/SageMaker-Pipelines-Step-By-Step/tree/main/phase01
- https://github.com/gonsoomoon-ml/SageMaker-Pipelines-Step-By-Step/tree/main/phase02
- https://docs.aws.amazon.com/sagemaker/latest/dg/build-and-manage-parameters.html
- https://aws.amazon.com/ko/blogs/machine-learning/use-deep-learning-frameworks-natively-in-amazon-sagemaker-processing/
- https://docs.aws.amazon.com/ko_kr/sagemaker/latest/dg/build-and-manage-steps.html#step-type-processing
- https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-sdk.html (SageMaker Pipelines SDK)
- https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-caching.html (Caching Pipeline Steps)
- https://aws.amazon.com/de/blogs/machine-learning/use-a-sagemaker-pipeline-lambda-step-for-lightweight-model-deployments/ (AWS AIML Blog: Use a SageMaker Pipeline Lambda step for lightweight model deployments) 
- https://github.com/aws-samples/mlops-sagemaker-github-actions
