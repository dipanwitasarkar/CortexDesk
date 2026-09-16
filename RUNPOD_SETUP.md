# RunPod Public Endpoints Setup Guide

## 🚀 **Complete Setup Instructions**

### **Step 1: Get RunPod API Key**

1. **Go to:** https://console.runpod.io/
2. **Sign up** (free)
3. **Click "API Keys"** in the left sidebar
4. **Click "Create API Key"**
5. **Copy the key**

**That's it! You now have a RunPod API key.**

### **Step 2: Update Configuration**

1. **Edit `backend/.env`:**
   ```env
   DELL_LLM_ENDPOINT=https://api.runpod.ai/v2/qwen3-32b-awq/openai/v1
   DELL_LLM_API_KEY=your-actual-runpod-api-key
   DELL_LLM_MODEL=Qwen/Qwen3-32B-AWQ
   DELL_LLM_EMBEDDING_MODEL=Qwen/Qwen3-32B-AWQ
   ```

2. **Replace `your-actual-runpod-api-key`** with your actual RunPod API key

### **Step 3: Test the Configuration**

1. **Run the test script:**
   ```bash
   cd backend
   python3 test_runpod_config.py
   ```

2. **Expected output:**
   ```
   === RunPod Public Endpoints Configuration Test ===

   1. Checking environment variables:
      DELL_LLM_ENDPOINT: https://api.runpod.ai/v2/qwen3-32b-awq/openai/v1
      DELL_LLM_API_KEY: your-key... (truncated)
      DELL_LLM_MODEL: Qwen/Qwen3-32B-AWQ

   2. Testing RunPod connection:
      ✓ OpenAI client initialized

   3. Testing chat completion:
      ✓ Chat completion successful
      Response: Yes, I can hear you

   === Test Complete ===
   ```

### **Step 4: Start the Windows AI Assistant**

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

3. **Start frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### **Step 5: Test the Assistant**

1. **Open browser:** http://localhost:5173
2. **Send a message:** "Hello, can you help me?"
3. **You should get a fast response** from RunPod

## 🎯 **About RunPod Public Endpoints**

**What it is:**
- Pre-deployed AI models on RunPod infrastructure
- No setup required
- OpenAI-compatible API
- Pay per usage

**Model we're using:**
- **Qwen3 32B AWQ** - Advanced LLM with reasoning capabilities
- **Cost:** $10 per 1M tokens
- **Quality:** Excellent
- **Speed:** Fast

## 📊 **Cost Comparison**

| Service | Cost | Speed | Quality | Setup |
|---------|------|-------|---------|-------|
| **RunPod** | $10/1M tokens | ⚡⚡⚡⚡ | Excellent | Very Easy |
| **Groq** | Free | ⚡⚡⚡⚡⚡ | Excellent | Very Easy |
| **OpenAI** | $0.03/1K tokens | ⚡⚡⚡⚡ | Excellent | Easy |
| **Hugging Face** | Variable | ⚡⚡⚡ | Good | Medium |

**Cost examples for RunPod:**
- 1,000 tokens: $0.01
- 10,000 tokens: $0.10
- 100,000 tokens: $1.00
- 1,000,000 tokens: $10.00

## 🎯 **Available RunPod Models**

**Text models:**
- **Qwen3 32B AWQ** - Advanced reasoning (recommended)
- **IBM Granite** - Enterprise-focused
- **Moonshot Kimi** - General purpose

**Image models:**
- Flux Dev, Flux Schnell
- Qwen Image
- And many more

**Video models:**
- WAN 2.5, WAN 2.6
- Kling v2.1
- SORA 2

## 🔧 **Troubleshooting**

### **API Key Error**

**Error:** "Invalid API key" or "Unauthorized"

**Solution:**
- Check your API key is correct
- Make sure it's from RunPod console
- Generate a new key if needed

### **Connection Error**

**Error:** "Connection refused" or "Timeout"

**Solution:**
- Check your internet connection
- Verify the endpoint URL is correct
- Try again (RunPod might be temporarily down)

### **Model Not Found**

**Error:** "Model not found"

**Solution:**
- Check the model name is correct
- Use the exact model name from RunPod docs
- Check if the model is available

### **Slow Response**

**If response is slow:**
- Check your internet connection
- Try a different model
- Check RunPod status page

## 💡 **Tips**

1. **Use Qwen3 32B AWQ** for best quality
2. **Monitor usage** in RunPod console
3. **Set budget alerts** to avoid surprises
4. **Cache responses** when possible
5. **Use streaming** for better UX

## 🎯 **What's Local vs Cloud**

**Local (Your VM):**
- ✅ Backend server
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Qdrant vector database
- ✅ File storage
- ✅ All your data

**Cloud (RunPod):**
- ❌ LLM inference only
- ✅ Fast inference
- ✅ Excellent quality
- ✅ Pay per usage
- ✅ No setup required

**Privacy:**
- Your data stays local (except prompts sent to RunPod)
- RunPod doesn't store data permanently
- Check RunPod's privacy policy

## 🚀 **Next Steps**

After setup:

1. **Test thoroughly** with different queries
2. **Monitor usage** in RunPod console
3. **Set budget alerts**
4. **Implement caching** to reduce costs
5. **Monitor costs** regularly

## 🆘 **Getting Help**

If you have issues:
1. Check the test script output
2. Check RunPod console for status
3. Check RunPod documentation
4. Review the logs in your backend

---

**Your Windows AI Assistant is now ready with RunPod Public Endpoints!**
