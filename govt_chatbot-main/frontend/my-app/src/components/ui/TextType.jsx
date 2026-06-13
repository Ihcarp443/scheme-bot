'use client';

import {
  useEffect,
  useRef,
  useState,
  createElement,
  useMemo,
  useCallback
} from 'react';
import { gsap } from 'gsap';

const TextType = ({
  text,
  as: Component = 'div',
  typingSpeed = 50,
  initialDelay = 0,
  className = '',
  showCursor = true,
  cursorCharacter = '|',
  cursorClassName = '',
  cursorBlinkDuration = 0.5,
  textColors = [],
  variableSpeed,
  onComplete, // ✅ new callback
  startOnVisible = false,
  reverseMode = false,
  ...props
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(!startOnVisible);
  const [isDone, setIsDone] = useState(false); // ✅ track completion

  const cursorRef = useRef(null);
  const containerRef = useRef(null);

  const textArray = useMemo(() => {
    if (!text) return [''];
    return Array.isArray(text) ? text : [text];
  }, [text]);

  const getRandomSpeed = useCallback(() => {
    if (!variableSpeed) return typingSpeed;
    const { min = 20, max = 60 } = variableSpeed;
    return Math.random() * (max - min) + min;
  }, [variableSpeed, typingSpeed]);

  const getCurrentTextColor = () => {
    if (textColors.length === 0) return 'inherit';
    return textColors[0];
  };

  // visibility observer
  useEffect(() => {
    if (!startOnVisible || !containerRef.current) return;

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) setIsVisible(true);
      });
    });

    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [startOnVisible]);

  // cursor blink (only while typing)
  useEffect(() => {
    if (!showCursor || !cursorRef.current) return;

    gsap.set(cursorRef.current, { opacity: 1 });

    gsap.to(cursorRef.current, {
      opacity: 0,
      duration: cursorBlinkDuration,
      repeat: -1,
      yoyo: true,
      ease: 'power2.inOut'
    });
  }, [showCursor, cursorBlinkDuration]);

  // typing logic (NO DELETE ANYMORE)
  useEffect(() => {
    if (!isVisible || isDone) return;

    let timeout;

    const fullText = textArray[0] || '';
    const processedText = reverseMode
      ? fullText.split('').reverse().join('')
      : fullText;

    const type = () => {
      if (currentCharIndex < processedText.length) {
        timeout = setTimeout(() => {
          setDisplayedText(prev => prev + processedText[currentCharIndex]);
          setCurrentCharIndex(prev => prev + 1);
        }, variableSpeed ? getRandomSpeed() : typingSpeed);
      } else {
        setIsDone(true);
        onComplete?.();
      }
    };

    if (currentCharIndex === 0 && displayedText === '') {
      timeout = setTimeout(type, initialDelay);
    } else {
      type();
    }

    return () => clearTimeout(timeout);
  }, [
    currentCharIndex,
    displayedText,
    typingSpeed,
    initialDelay,
    textArray,
    isVisible,
    isDone,
    reverseMode,
    variableSpeed,
    onComplete
  ]);

  // cursor should disappear after completion
  const shouldShowCursor = showCursor && !isDone;

  return createElement(
    Component,
    {
      ref: containerRef,
      className: `inline-block whitespace-pre-wrap tracking-tight ${className}`,
      ...props
    },
    <>
      <span
        className="inline"
        style={{ color: getCurrentTextColor() }}
      >
        {displayedText}
      </span>

      {shouldShowCursor && (
        <span
          ref={cursorRef}
          className={`ml-1 inline-block ${cursorClassName}`}
        >
          {cursorCharacter}
        </span>
      )}
    </>
  );
};

export default TextType;

// thread-grpah-state
// StateSnapshot(values={'input_text': 'all good', 'input_type': 'text', 'user_lang': 'en-IN', 'query_en': 'all good', 'answer_en': 'Glad to hear that! 😊 Is there anything else I can help you with today?', 'final_answer': 'Glad to hear that! 😊 Is there anything else I can help you with today?', 'intent': 'general', 'issue_type': None, 'complaint_data': {'issue_type': None}, 'messages': [HumanMessage(content='hi how are you', additional_kwargs={}, response_metadata={}, id='0e94475f-f3fb-4cf1-85f1-3a2dc00b8bef'), AIMessage(content="I'm doing well, thank you for asking! How are you doing today?", additional_kwargs={}, response_metadata={}, id='62863e80-f6cd-4d2f-a809-d921d3ef74d2', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='translate your anwer to hindi', additional_kwargs={}, response_metadata={}, id='cdb86669-3a97-460a-b8c6-9cb300d04126'), AIMessage(content='मैं ठीक हूँ, पूछने के लिए धन्यवाद! आप आज कैसे हैं?', additional_kwargs={}, response_metadata={}, id='5702fec4-7b20-4935-b8a5-5ed6359f76a8', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='transslate it to hindi', additional_kwargs={}, response_metadata={}, id='0fbb0127-41f3-4f1e-9352-d589ff23d517'), AIMessage(content='Since you didn\'t specify a new sentence, I assume you mean the original answer:\n\n**"मैं ठीक हूँ, पूछने के लिए धन्यवाद! आप आज कैसे हैं?"**\n\n(Pronunciation: *Main theek hoon, poochne ke liye dhanyavaad! Aap aaj kaise hain?*)', additional_kwargs={}, response_metadata={}, id='84fa64d1-6dc0-45df-8a83-0285745ed3d6', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content="Comment allez-vous aujourd'hui?", additional_kwargs={}, response_metadata={}, id='a2abd4c0-f582-4ea3-a92c-68cd8e16eaa1'), AIMessage(content='Je vais très bien, merci ! Et vous, comment allez-vous ?', additional_kwargs={}, response_metadata={}, id='4fbdc33f-a4d9-4a41-b403-8d5cb51212e3', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='all good', additional_kwargs={}, response_metadata={}, id='b85ef5c7-5e31-4949-ad42-ecffbd1ae45a'), AIMessage(content='Glad to hear that! 😊 Is there anything else I can help you with today?', additional_kwargs={}, response_metadata={}, id='5f469e42-7af3-445b-b36e-5ebaa211b6a6', tool_calls=[], invalid_tool_calls=[])], 'chat_history': [{'role': 'user', 'text': 'hi how are you', 'lang': 'en-IN'}, {'role': 'assistant', 'text': "I'm doing well, thank you for asking! How are you doing today?", 'lang': 'en-IN'}, {'role': 'user', 'text': 'translate your anwer to hindi', 'lang': 'en-IN'}, {'role': 'assistant', 'text': "I'm doing well, thank you for asking! Comment allez-vous aujourd'hui?", 'lang': 'en-IN'}, {'role': 'user', 'text': 'transslate it to hindi', 'lang': 'en-IN'}, {'role': 'assistant', 'text': 'Since you didn\'t specify a new sentence, I assume you mean the original answer:\n\n**"मैं ठीक हूँ, पूछने के लिए धन्यवाद! आप आज कैसे हैं?"**\n\n(Pronunciation: *Main theek hoon, poochne ke liye dhanyavaad! Aap aaj kaise hain?*)', 'lang': 'en-IN'}, {'role': 'user', 'text': 'आप आज कैसे हैं ?', 'lang': 'hi-IN'}, {'role': 'assistant', 'text': 'यदि यह आपके लिए उपयुक्त है, तो बहुत अच्छा है! कोई बात नहीं, आपकी क्या राय है?', 'lang': 'hi-IN'}, {'role': 'user', 'text': 'all good', 'lang': 'en-IN'}, {'role': 'assistant', 'text': 'Glad to hear that! 😊 Is there anything else I can help you with today?', 'lang': 'en-IN'}]}, next=(), config={'configurable': {'thread_id': 'dde479ad-3711-49e1-a47f-0f2683acea19', 'checkpoint_ns': '', 'checkpoint_id': '1f16703f-0a7e-6647-801c-6c308fa514ba'}}, metadata={'source': 'loop', 'step': 28, 'parents': {}}, created_at='2026-06-13T08:43:24.529415+00:00', parent_config={'configurable': {'thread_id': 'dde479ad-3711-49e1-a47f-0f2683acea19', 'checkpoint_ns': '', 'checkpoint_id': '1f16703f-08d0-6d5e-801b-f20d825e8dee'}}, tasks=(), interrupts=())
// INFO:     127.0.0.1:60671 - "GET /threads/dde479ad-3711-49e1-a47f-0f2683acea19 HTTP/1.1" 200 OK