FROM public.ecr.aws/lambda/python:3.10

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -t .

# Download and link spaCy model
RUN python -m spacy download en_core_web_md \
 && python -m spacy link en_core_web_md en_core_web_md

# Copy source code (your redactPIIData.py)
COPY redactPIIData.py .

# Set CMD to handler
CMD ["redactPIIData.lambda_handler"]
