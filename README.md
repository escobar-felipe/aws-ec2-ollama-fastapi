# AWS EC2 CUDA Ollama Setup

This guide outlines the steps to set up an Ollama API service on an AWS EC2 instance with CUDA support.

## 1. Launch EC2 Instance

a. Go to EC2 dashboard and click "Launch instance"
b. Name your instance (e.g., "Ollama-GPU-Server")
c. AMI: Search for and select "Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)"
d. Instance type: g4dn.xlarge (4 vCPUs, 16 GiB Memory, 1 GPU)
e. Create or select a key pair for SSH access
f. Network settings: Create a security group with the following rules:
   - Allow SSH (port 22) from your IP
   - Allow Custom TCP (port 8080) from anywhere (0.0.0.0/0)
g. Configure storage: At least 30 GiB
h. Launch the instance

## 2. Connect to EC2 Instance

```
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## 3. Update System And install python

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
```


## 5. Install Ollama

```
curl -fsSL https://ollama.com/install.sh | sh
```

## 6. Clone Repository and create a virtual env

```
git clone https://github.com/escobar-felipe/aws-ec2-ollama-fastapi.git
cd aws-ec2-ollama-fastapi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 7. Start Ollama in Background

```
ollama serve 
```

## 8. Pull Gemma Model

```
ollama pull gemma2:2b
```

## 9. Run Python FastAPi Application

```
python main.py
```

## 10. Set Up Systemd Service (Optional)

Create service file:
```
sudo nano /etc/systemd/system/fastapi.service
```

Add the following content:
```
[Unit]
Description=FastAPI Proxy Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/aws-ec2-ollama-fastapi
ExecStart=/home/ubuntu/aws-ec2-ollama-fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```
sudo systemctl enable fastapi.service
sudo systemctl start fastapi.service
```

## 11. Test API

From your local machine:
```
curl http://ec2-your-ec2.amazonaws.com:8080/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer demo" \
-d '{
  "model": "gemma2:2b",
  "messages": [
    {"role": "user", "content": "Tell me a story about a brave knight"}
  ],
  "stream": true
}'
```

## Troubleshooting

- Ensure EC2 instance is running
- Verify Python application is running
- Check port 8080 is open in EC2 security group
- Confirm Ollama is running and "gemma2:2b" model is available

To check service status:
```
sudo systemctl status fastapi.service
```