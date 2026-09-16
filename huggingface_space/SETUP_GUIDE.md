# Hugging Face Space Setup Guide

## 📋 **Complete Setup Instructions**

### **Step 1: Configure Your Space Settings**

1. **Go to your Space** on Hugging Face
2. **Click "Settings"** tab
3. **Set the following:**
   - **Space type**: Docker
   - **SDK**: Python
   - **Hardware**: T4 small (free tier)
   - **License**: MIT
   - **Secrets**: (optional, not needed for this setup)
4. **Click "Save"**

### **Step 2: Upload Files to Your Space**

You have two options:

#### **Option A: Upload via Web Interface**

1. **Go to your Space** on Hugging Face
2. **Click "Files"** tab
3. **Click "Upload files"**
4. **Upload these files:**
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `README.md`

#### **Option B: Upload via Git**

1. **Clone your Space:**
   ```bash
   git clone https://huggingface.co/spaces/your-username/your-space-name
   cd your-space-name
   ```

2. **Copy the files:**
   ```bash
   cp /path/to/huggingface_space/* .
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add LLM server"
   git push
   ```

### **Step 3: Wait for Build**

1. **Go to your Space** on Hugging Face
2. **Click "Logs"** tab to see the build progress
3. **Wait for the build to complete** (this can take 5-15 minutes)
4. **The Space will start automatically** after build

### **Step 4: Get Your Space URL**

Your Space URL will be:
```
https://your-username-your-space-name.hf.space
```

For example:
```
https://john-doe-windows-ai-assistant.hf.space
```

### **Step 5: Test Your Space**

1. **Open your Space URL** in a browser
2. **You should see:** `{"status":"running","model":"mistralai/Mistral-7B-Instruct-v0.2","device":"cuda"}`

3. **Test the health endpoint:**
   ```
   https://your-space-url/health
   ```

4. **Test the chat endpoint:**
   ```bash
   curl -X POST https://your-space-url/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"role": "user", "content": "Hello!"}],
       "temperature": 0.7,
       "max_tokens": 50
     }'
   ```

### **Step 6: Configure Windows AI Assistant**

1. **Edit `backend/.env`:**
   ```env
   DELL_LLM_ENDPOINT=https://your-space-url/v1
   DELL_LLM_API_KEY=
   DELL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   DELL_LLM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

2. **Replace `your-space-url`** with your actual Space URL

### **Step 7: Test Windows AI Assistant**

1. **Start infrastructure:**
   ```bash
   cd infrastructure
   podman-compose up -d
   ```

2. **Start backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 -m uvicorn app.main:app --reload
   ```

3. **Test the API:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/assistant \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, can you hear me?",
       "user_id": 1
     }'
   ```

## 🔧 **Troubleshooting**

### **Build Fails**

**Check the Logs:**
1. Go to your Space
2. Click "Logs" tab
3. Look for error messages

**Common Issues:**
- **Out of memory**: The T4 has 16GB VRAM, Mistral 7B fits fine
- **Timeout**: Build can take 10-15 minutes, be patient
- **Dependencies**: Check requirements.txt has correct versions

### **Space Won't Start**

**Check:**
1. Hardware is set to "T4 small"
2. Space type is "Docker"
3. All files are uploaded
4. No syntax errors in app.py

### **API Returns Errors**

**Check:**
1. Space URL is correct
2. Space is running (check logs)
3. Model is loaded (check logs)
4. Endpoint path is correct

### **Slow Response**

**Normal behavior:**
- First request: 5-10 seconds (model loading)
- Subsequent requests: 1-3 seconds
- T4 GPU is not the fastest, but it's free

## 📊 **Space Limitations**

**Free Tier Limits:**
- **GPU**: T4 small (16GB VRAM)
- **RAM**: ~30GB
- **Storage**: ~50GB
- **Requests**: No hard limit, but be reasonable
- **Uptime**: Generally good, but can go down

**Model Recommendations:**
- ✅ **Mistral 7B** - Works great
- ✅ **Llama 2 7B** - Works great
- ✅ **Gemma 7B** - Works great
- ❌ **Mistral 8x7B** - Too large (may OOM)
- ❌ **Llama 2 13B** - Too large (may OOM)

## 🎯 **Next Steps**

After your Space is running:

1. **Test it thoroughly** with the test script
2. **Monitor the logs** for any issues
3. **Check usage** in Hugging Face dashboard
4. **Consider upgrading** if you need more power

## 💡 **Tips**

- **Keep the Space public** for free tier
- **Use a smaller model** if you have issues
- **Monitor GPU usage** in the logs
- **Restart the Space** if it gets stuck
- **Use the /health endpoint** for monitoring

## 🆘 **Getting Help**

If you have issues:
1. Check the Space logs
2. Check the Hugging Face documentation
3. Ask in the Hugging Face community
4. Check the Dockerfile and requirements.txt

---

**Your Space is now ready to serve as the LLM backend for your Windows AI Assistant!**
