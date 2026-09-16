# Groq Setup Guide for Windows AI Assistant

## 🚀 **Complete Setup Instructions**

### **Step 1: Get Groq API Key**

1. **Go to:** https://console.groq.com/
2. **Sign up** (free, no credit card required)
3. **Click "API Keys"** in the left sidebar
4. **Click "Create API Key"**
5. **Copy the key** (starts with `gsk_`)

**That's it! You now have a free API key.**

### **Step 2: Update Configuration**

1. **Edit `backend/.env`:**
   ```env
   DELL_LLM_ENDPOINT=https://api.groq.com/openai/v1
   DELL_LLM_API_KEY=gsk_your-actual-api-key-here
   DELL_LLM_MODEL=llama-3.1-8b-instant
   DELL_LLM_EMBEDDING_MODEL=llama-3.1-8b-instant
   ```

2. **Replace `gsk_your-actual-api-key-here`** with your actual Groq API key

### **Step 3: Test the Configuration**

1. **Run the test script:**
   ```bash
   cd backend
   python3 test_groq_config.py
   ```

2. **Expected output:**
   ```
   === Groq Configuration Test ===

   1. Checking environment variables:
      DELL_LLM_ENDPOINT: https://api.groq.com/openai/v1
      DELL_LLM_API_KEY: gsk_xxxxxxxxxxxxx... (truncated)
      DELL_LLM_MODEL: llama-3.1-8b-instant

   2. Testing Groq connection:
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
3. **You should get a fast response** from Groq

## 🎯 **Available Groq Models**

**Recommended models for Windows AI Assistant:**

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama-3.1-8b-instant** | 8B | ⚡⚡⚡⚡⚡ | Excellent | General purpose (recommended) |
| **llama-3.1-70b-versatile** | 70B | ⚡⚡⚡⚡ | Excellent | Complex tasks |
| **mixtral-8x7b-32768** | 7B | ⚡⚡⚡⚡ | Excellent | General purpose |
| **gemma-7b-it** | 7B | ⚡⚡⚡⚡ | Good | General purpose |

**To change models:**
```env
DELL_LLM_MODEL=llama-3.1-70b-versatile
```

## 📊 **Groq vs Alternatives**

| Feature | Groq | Hugging Face | OpenAI | Local |
|---------|------|--------------|--------|-------|
| **Cost** | Free | Pay per token | Pay per token | Free (if you have GPU) |
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡ (if GPU) |
| **Setup** | Very Easy | Medium | Easy | Hard |
| **Quality** | Excellent | Good | Excellent | Excellent |
| **Your VM** | ✅ Works | ❌ Issues | ✅ Works | ❌ No GPU |

## 🔧 **Troubleshooting**

### **API Key Error**

**Error:** "Invalid API key"

**Solution:**
- Check your API key is correct
- Make sure it starts with `gsk_`
- Generate a new key if needed

### **Connection Error**

**Error:** "Connection refused" or "Timeout"

**Solution:**
- Check your internet connection
- Verify the endpoint URL is correct
- Try again (Groq might be temporarily down)

### **Model Not Found**

**Error:** "Model not found"

**Solution:**
- Check the model name is correct
- Use one of the recommended models
- Check Groq documentation for available models

### **Slow Response**

**If response is slow:**
- Check your internet connection
- Try a different model (some are faster)
- Check Groq status page

## 💡 **Tips**

1. **Use llama-3.1-8b-instant** for best speed/quality balance
2. **Monitor usage** in Groq console (free tier is generous)
3. **Keep API key secret** - don't commit it to git
4. **Use streaming** for better user experience
5. **Cache responses** when possible

## 🎯 **What's Local vs Cloud**

**Local (Your VM):**
- ✅ Backend server
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Qdrant vector database
- ✅ File storage
- ✅ All your data

**Cloud (Groq):**
- ❌ LLM inference only
- ✅ Ultra-fast (500 tokens/second)
- ✅ Free
- ✅ Excellent quality

**Privacy:**
- Your data stays local (except the prompt sent to Groq)
- Groq doesn't store your data permanently
- You can check Groq's privacy policy

## 🚀 **Next Steps**

After setup:

1. **Test thoroughly** with different queries
2. **Monitor performance** in Groq console
3. **Try different models** to find the best fit
4. **Implement caching** to reduce API calls
5. **Monitor costs** (though free tier is generous)

## 🆘 **Getting Help**

If you have issues:
1. Check the test script output
2. Check Groq console for status
3. Check Groq documentation
4. Review the logs in your backend

---

**Your Windows AI Assistant is now ready with Groq!**
