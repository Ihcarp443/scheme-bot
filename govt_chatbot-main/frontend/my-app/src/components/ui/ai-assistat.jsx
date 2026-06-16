import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, X, Loader2 ,Mic, Square, Trash,NotebookPen  , PlusCircleIcon ,Volume2,Paperclip} from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatSkeleton } from "./ChatSkelton";
import TextType from "./TextType";
import {
  ThumbsUp,
  ThumbsDown,
  Copy,
  RotateCcw,
} from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
const AIMessageBar = () => {
  // const BASE_URL = process.env.ENDPOINT;
  const BASE_URL = process.env.NEXT_PUBLIC_ENDPOINT || "http://50.19.164.128:8000";
  const BASE_URL_2 = process.env.NEXT_PUBLIC_ENDPOINT_2;
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const[threadID,set_threadID]=useState("")
  const [isSpeaking, setIsSpeaking] = useState(false);
  const fileInputRef = useRef(null);
  // adding threads
  const [threads, setThreads] = useState([]);
  const [interrupt, setInterrupt] = useState(false);
  const [interruptData, setInterruptData] = useState(null);
  const [selectedThread, setSelectedThread] =useState(null);
  const[loadPastChat,setloadPastChat]=useState(false)


  // const submitFeedback = async (
  //   msg,
  //   feedback
  // ) => {
  //   try {
  //     await fetch(
  //       `${BASE_URL}/feedback`,
  //       {
  //         method: "POST",
  //         headers: {
  //           "Content-Type":
  //             "application/json",
  //         },
  //         body: JSON.stringify({
  //           thread_id: threadID,
  //           answer: msg.text,
  //           feedback,
  //         }),
  //       }
  //     );

  //     toast.success(
  //       "Feedback submitted"
  //     );

  //   } catch (err) {
  //     console.error(err);
  //   }
  // };
  const submitFeedback = async (
  msg,
  feedback
) => {
  try {

    if (msg.feedback) {
      toast.info(
        "Feedback already submitted"
      );
      return;
    }

    await fetch(
      `${BASE_URL}/feedback`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          thread_id: threadID,
          answer: msg.text,
          feedback,
        }),
      }
    );

    setMessages(prev =>
      prev.map(m =>
        m === msg
          ? { ...m, feedback }
          : m
      )
    );

    toast.success(
      "Feedback submitted"
    );

  } catch (err) {
    console.error(err);
  }
};
  const resumeInterrupt = async(userInput) => {

  try {  
    setIsTyping(true);
    const field =interruptData.missing_fields[0];
    console.log("userInturrp",userInput)
    if(isNaN(userInput)){
      setIsTyping(false);
      toast.warning("Applicatio ID should be Number.")

      return
    }
    const payload = {
      thread_id: String(threadID),
      data: {
        [field]: userInput
      }
    };

    const response = await fetch(
      `${BASE_URL}/grievance/resume`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      }
    );
    setIsTyping(false);
    const res = await response.json();

    console.log(res);

    // Another interrupt
    if (res.status === "interrupt") {

      setInterruptData(res.interrupt);
      user_lang=res.user_lang;
      setMessages(prev => [
        ...prev,
        ...res.interrupt.questions.map(q => ({
          text: q,
          isUser: false,
          lang:user_lang,
        }))
      ]);

      return;
    }

    // Completed
    setInterrupt(false);
    setInterruptData(null);

    setMessages(prev => [
      ...prev,
      {
        text: res.answer,
        isUser: false
      }
    ]);
  } catch(err) {
    setIsTyping(false);
    toast.error("Something went wrong !")
    console.error(err);
  }
};
  const loadThreads = async () => {
    try {
      const response = await fetch(
        `${BASE_URL}/threads/`
      );

      const res = await response.json();

      if (res.success) {
        setThreads(res.threads);
      }
    } catch (error) {
      console.error(
        "Failed to load threads",
        error
      );
    }
};
  const loadThreadMessages = async (threadId) => {
    setloadPastChat(true)
    try {
      setSelectedThread(threadId);
      const response = await fetch(
        `${BASE_URL}/threads/${threadId}`
      );

      const res = await response.json();

      if (!res.success){
        setloadPastChat(false)
        return;
      }

      const state = res.state;

      const restoredMessages =
        (state.chat_history || []).map((msg) => ({
          text: msg.text,
          isUser: msg.role === "user",
          animate:false,
          lang:msg.lang
        }));
        setTimeout(()=>{
            setloadPastChat(false)
        },2000)
        
        setMessages(restoredMessages);

      // continue conversation in same thread
      set_threadID(threadId);
      

    } catch (error) {
      console.error(error);
    }
};


  
  useEffect(() =>{
    loadThreads();
  }, []);





  
  const sendTextToBackend = async(userMessage,input_t) =>{
      setIsTyping(true);
      // console.log(userMessage)
    //  const id=localStorage.getItem("user_id") || "user01"
     const id="0011"
    try 
    {
      const data = {
                  message: userMessage,
                  thread_id: threadID|| null,
                  input_type:input_t,
                  user_id:id
                };
      // console.log("data",data)

    const response = await fetch(
      `${BASE_URL}/chat/chat`,
       {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
      }
    );
    // console.log("body",body)
    const res = await response.json();
    console.log(res)
    if(res.success)
    {
      if (res.thread_id)
      {
        set_threadID(res.thread_id);
      }
      await loadThreads();
  
      console.log("Backend Response:", res);

      if (res.interrupt)
      {
        console.log("Received interrupt");
        setInterrupt(true);
        setInterruptData(res.data);

        setMessages(prev => [
          ...prev,
          ...res.data.questions.map(q => ({
            text: q,
            isUser: false,
            animate:true,
            lang:q.user_lang,
          }))
        ]);

        setIsTyping(false);
        return;
      }
      setIsTyping(false)
      const fin=res.answer
      const user_lang=res.user_lang
      setMessages((prev) => [...prev, { text: fin, isUser: false ,animate:true ,lang:user_lang}]);
      if (input_t === "audio" && res.audio) {
        const audio = new Audio(`data:audio/wav;base64,${res.audio}`);
        audio.play();
        // playBase64Audio(res.audio);
      }
    }
    else{
      setIsTyping(false)
      if(res.error == "Translation failed"){
        toast.error("This Language is not supported, Try some other languages.")
        return
      }
      toast.error("Can't fetch answer Try again!")
    }
   } catch (error) {
    console.error(error);
    toast.error("Something went wrong")
   }
  };

  const handleSubmit = (e) =>{
        e?.preventDefault();
        if (input.trim() === "") return;
        const userMessage = input;
        setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
        setInput("");
        if(interrupt)
        {
            resumeInterrupt(userMessage);
        }
        else
        {
            sendTextToBackend(
              userMessage,
              "text"
            );
          }
      };
  
const handleDeleteThread = async (threadId) => {
  try {
    const res = await fetch(
      `${BASE_URL}/threads/${threadId}`,
      {
        method: "DELETE",
      }
    );

    const data = await res.json();

    if (data.success) {
      setThreads((prev) =>
        prev.filter((t) => t.thread_id !== threadId)
      );
      toast.success("Chat deleted Successfully")
      if (selectedThread === threadId) {
        setSelectedThread(null);
        setMessages([]);
        set_threadID(null);
      }
    }
  } catch (error) {
    console.error(error);
    toast.error("Chat could not be deleted. Try again!")
  }
};
  const [isRecording, setIsRecording] = useState(false);
  const RECORDING_DURATION = 10000; // 10 seconds
  const recordingTimeoutRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const intervalRef = useRef(null);
  
  const startRecording = async () => {
      setTimeLeft(RECORDING_DURATION / 1000);

      clearInterval(intervalRef.current);

      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(intervalRef.current);
            return 0;
          }
        
          return prev - 1;
        });
      }, 1000);

  try
    {
      const stream = await navigator.mediaDevices.getUserMedia(
      {
        audio: true,
      });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
    
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      mediaRecorder.onstop = async () => {
        clearInterval(intervalRef.current);
      
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
      
        await sendAudioToBackend(audioBlob);
      
        stream.getTracks().forEach((track) => track.stop());
      
        setTimeLeft(0);
        setIsRecording(false);
      };
    
      mediaRecorder.start();
      setIsRecording(true);
    
      recordingTimeoutRef.current = setTimeout(() => {
        if(mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") 
        {
          mediaRecorderRef.current.stop();
        }
      }, RECORDING_DURATION);

   }
   catch (error) 
   {
    console.error(error);
   }
};

const stopRecording = () => {
  if (
    mediaRecorderRef.current &&
    mediaRecorderRef.current.state === "recording"
  ) {
    clearTimeout(recordingTimeoutRef.current);
    clearInterval(intervalRef.current);

    mediaRecorderRef.current.stop();

    setTimeLeft(0);
    setIsRecording(false);
  }
};

const handleAudioUpload = async (e) => {
  const file = e.target.files[0];

  if (!file) return;

  if (!file.type.startsWith("audio/")) {
    toast.error("Please upload an audio file");
    return;
  }

  try {
    await sendAudioToBackend(file);
  } catch (error) {
    console.error(error);
    toast.error("Failed to upload audio");
  }

  // reset input so same file can be selected again
  e.target.value = "";
};

useEffect(() => {
  return () => {
    clearTimeout(recordingTimeoutRef.current);
    clearInterval(intervalRef.current);
  };
}, []);

const sendAudioToBackend = async (audioBlob) => {
  try {
    const formData = new FormData();

    formData.append(
      "audio",
      audioBlob,
      `recording-${Date.now()}.webm`
    );
    console.log("Sending audio")
    const response = await fetch(
      // `${BASE_URL}/upload-audio`,
      `${BASE_URL}/audio/transcribe`,
      {
        method: "POST",
        body: formData,
      }
    );

    // const data = await response.json();
    // console.log("Backend Response:", data);
    console.log("TRANSCRIPT CAME:")
    const res = await response.json();
    console.log("Backend Response:", res);
    const transcript =res.transcript.transcript
    setMessages((prev) => [...prev, { text: transcript, isUser: true }]);
    sendTextToBackend(transcript,"audio")
   } catch (error) {
    console.error(error);
   }
  };

  const clearChat = () => {
    setMessages([]);
    set_threadID(null);
    setSelectedThread(null);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  const speakText = async(text,lang) => {
    try 
    {
      console.log(text)
      console.log(lang)
    const response = await fetch(`${BASE_URL}/play/dictate_text`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_lang: lang,
        text: text,
      }),
    });

    const data = await response.json();
    console.log(data)
    if (data.success) {
      console.log("Audio received:", data.audio);
      const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
       setTimeout(() => {
    
    audio.play();
  }, 1000);

    } else {
      console.error("Error:", data.error);
    }

  } catch (error) {
    console.error("API call failed:", error);
  }
  // const speech = new SpeechSynthesisUtterance(text);

  // speech.lang = "hi-IN";
  // speech.rate = 1;
  // speech.pitch = 1;

  // window.speechSynthesis.cancel(); // stop previous speech
  // window.speechSynthesis.speak(speech);
};



return (
  <>
    
    {/* <div className="h-screen bg-slate-950 flex justify-center">
      <Toaster richColors position="top-center" />
      <div className="w-full max-w-5xl flex flex-col h-full"> */}

  <div className="h-screen bg-slate-950 overflow-hidden">
  <Toaster richColors position="top-center" />

  <div className="flex h-full">
    {/* Sidebar CHAT HISTORY SECTION */}
    <div className="w-[30%] bg-slate-900 border-r border-slate-800 flex flex-col">

      <div className="p-5 border-b border-slate-800">
  <div className="flex items-center justify-between">
    <h2 className="text-white text-2xl font-semibold">
      Chat History
    </h2>

    <button
      onClick={clearChat}
      className="
        flex items-center gap-2
        px-3 py-2
        rounded-lg
        bg-slate-800
        text-slate-200
        hover:bg-slate-700
        hover:text-white
        transition-all duration-200
        cursor-pointer
      "
    >
      <NotebookPen size={18} strokeWidth={2} />
      <span className="text-sm font-medium">
        New Chat
      </span>
    </button>
  </div>
</div>
        {/* PAST CHATS */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">

        {threads.length === 0 ? (
          <p className="text-2xl text-slate-200 flex items-center justify-center">
            No Past Chats
          </p>
        ) : (
          threads.map((thread) => (
            <div
                key={thread.thread_id}
                onClick={() => loadThreadMessages(thread.thread_id)}
                className={`
                  rounded-lg p-3 cursor-pointer transition
                  ${
                    selectedThread === thread.thread_id
                      ? "bg-indigo-600"
                      : "bg-slate-800 hover:bg-slate-700"
                  }
                `}
              >
              
              <div className="text-white text-md font-medium truncate">
                {thread.title}
              </div>
                <div className=" flex justify-between">
                    <div className="text-slate-400 text-xs mt-1">
                      {thread.created_at}
                      </div>
                
                    <button
                         onClick={(e) => {
                           e.stopPropagation();
                           handleDeleteThread(thread.thread_id);
                         }}
                         className="text-slate-400 hover:text-red-500 ml-2 cursor-pointer"
                       >
                         <Trash size={20} />
                  </button>
              </div>

              
              
            
             
            </div>
          ))
        )}

      </div>
    </div>
    <div className="w-[70%] flex flex-col h-full ">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-8">
          {loadPastChat ? (
  <ChatSkeleton />
) :messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Sparkles className="h-14 w-14 text-indigo-400 mx-auto mb-4" />

                <h3 className="text-white text-2xl font-semibold mb-2">
                  How can I Assist you today?
                </h3>

                <p className="text-slate-400">
                  Let's resolve your queries and find best Schemes for you
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-[90%] mx-auto space-y-6 ">
              {messages.map((msg, index) => (
                <div
              key={index}
              className={`flex ${
                msg.isUser ? "justify-end" : "justify-start"
              }`}
            >
                <div className="group max-w-[75%]">
    
                <div
                  className={`
                    px-4
                    py-3
                    rounded-2xl
                    animate-fade-in
                    ${
                      msg.isUser
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-800 text-slate-100 border border-slate-700"
                    }
                  `}
                >
              <div
                className={`
                  text-md
                  leading-[1.6]
                  tracking-[0.2px]
                  [&_h1]:text-2xl
                  [&_h1]:font-bold
                  [&_h2]:text-xl
                  [&_h2]:font-semibold
                  [&_ul]:list-disc
                  [&_ul]:pl-5
                  [&_ol]:list-decimal
                  [&_ol]:pl-5
                  [&_li]:my-1
                  [&_p]:mb-2
                  [&_strong]:font-bold
                  ${!msg.user && msg.error ?
                    " text-red-400 font-semibold": ""
                  }
                  `}
              >
                {msg.isUser ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.text}
                    </ReactMarkdown       >

                  ) : msg.animate ? (
                    /* 🤖 AI MESSAGE → typing effect */
                    <TextType
                      text={msg?.text || ""}
                      typingSpeed={30}
                      // pauseDuration={50}
                      showCursor={true}
                      cursorCharacter="|"
                      variableSpeed={{
                        min: 10,
                        max: 25
                      }}
                    />
                  ):(
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.text}
                  </ReactMarkdown>
                )}
              </div>
            </div>
              {/* Feedback Buttons */}
                {!msg.isUser && (
                    <div
                      className="
                        flex
                        items-center
                        gap-1
                        mt-1
                        ml-1
                        transition-opacity
                        duration-200
                      "
                    >
                      <button
                        onClick={() =>
                          submitFeedback(msg, "like")
                        }
                        className="
                          p-1.5
                          rounded-md
                          text-slate-500
                          hover:text-green-400
                          hover:bg-slate-800
                          cursor-pointer
                        "
                      >
                        <ThumbsUp
                              size={14}
                              className={
                                msg.feedback === "like"
                                  ? "text-green-500"
                                  : ""
                              }
                            />
                      </button>

                      <button
                        onClick={() =>
                          submitFeedback(msg, "dislike")
                        }
                        className="
                          p-1.5
                          rounded-md
                          text-slate-500
                          hover:text-red-400
                          hover:bg-slate-800
                          cursor-pointer
                        "
                      >
                        <ThumbsDown
                          size={14}
                          className={
                            msg.feedback === "dislike"
                              ? "text-red-500"
                              : ""
                          }
                        />
                      </button>
                      
                    </div>
                    )}

                  </div>
                </div>
                      ))}

                      {isTyping && (
                        <div className="flex justify-start">
                          <div className="bg-slate-800 border border-slate-700 rounded-2xl px-4 py-3">
                            <div className="flex gap-2">
                              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce animation-duration:[0.5s]" />
                              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-100 animation-duration:[0.5s]" />
                              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-200 animation-duration:[0.5s]" />
                            </div>
                          </div>
                        </div>
                      )}

                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>
                
              {/* {CHAT BAR MODULE} */}

        <div
          className="bg-slate-950 p-4 "
        >
          <form
            onSubmit={handleSubmit}
            className="max-w-3xl mx-auto"
          >
            <div className="relative">
              <input
                type="file"
                ref={fileInputRef}
                accept="audio/*"
                onChange={handleAudioUpload}
                className="hidden"
              />
              
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Message AI Assistant..."
                className="
                  w-full
                  bg-slate-800
                  border
                  border-slate-700
                  rounded-3xl
                  py-4
                  pl-5
                  pr-14
                  text-white
                  placeholder:text-slate-400
                  focus:outline-none
                  focus:ring-2
                  focus:ring-indigo-500
                "
                onInput={(e) => {
                  e.currentTarget.style.height = "auto";
                  e.currentTarget.style.height = e.currentTarget.scrollHeight + "px";
                }}
              />
              
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current.click()}
                  className="
                    p-2
                    rounded-full
                    bg-slate-700
                    text-slate-200
                    hover:bg-slate-600
                    cursor-pointer
                  "
                >
                  <Paperclip className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={
                    isRecording
                      ? stopRecording
                      : startRecording
                  }
                  className={`
                    p-2
                    rounded-full
                    transition-colors
                    ${
                      isRecording
                        ? "bg-red-600 text-white"
                        : "bg-slate-700 text-slate-200 hover:bg-slate-600"
                    }
                  `}
                >
                  <div className="flex gap-1.5">
                  {isRecording ? (
                    <Square className="h-5 w-5" />
                  ) : (
                    <Mic className="h-5 w-5 cursor-pointer"  />
                  )}
                  {isRecording && (
                    <span className="text-white-400 text-md">
                      {timeLeft}s
                    </span>
                  )}
                  </div>
                </button>
                
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className={`
                    p-2
                    rounded-full
                    ${
                      !input.trim()
                        ? "bg-slate-700 text-slate-500"
                        : "bg-indigo-600 text-white hover:bg-indigo-500 cursor-pointer"
                    }
                  `}
                >
                  {isTyping ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
                
              </div>
            </div>
          </form>
        </div>
</div>
        {/* Input Section */}
        

        <style>
          {`
          @keyframes fade-in {
            from {
              opacity: 0;
              transform: translateY(8px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .animate-fade-in {
            animation: fade-in 0.3s ease-out forwards;
          }

          .delay-75 {
            animation-delay: 0.2s;
          }

          .delay-150 {
            animation-delay: 0.4s;
          }
        `}
        </style>
      </div>
    </div>
  </>
);
};

export default AIMessageBar;
