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


// 'intent': 'general', 'issue_type': None, 'complaint_data': {'issue_type': None}, 'messages': [HumanMessage(content="Monthly Musnadat Al Matluba Li Takdid Al Parnasah Tarabiya Til Ma'iz Lim Nisab.", additional_kwargs={}, response_metadata={}, id='9d5735db-73d9-4e07-b3aa-8b150605fa37'), AIMessage(content='I don’t know based on available data.', additional_kwargs={}, response_metadata={}, id='c5de8006-6500-4d4c-9336-e0f83aeb0f61', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='The Arabic translation of what are the latest schemes launched by the government is ما هي احادة المبادرات', additional_kwargs={}, response_metadata={}, id='d2947516-26ab-4d71-9c61-e690afa1029b'), AIMessage(content="The translation you provided is almost correct, but there is a typo. 'احادة' is not a word; it should be 'أحدث' (ahdath) for 'latest'. The correct translation would be: 'ما هي أحدث المبادرات التي أطلقتها الحكومة؟'", additional_kwargs={}, response_metadata={}, id='27ba700a-5dc3-4d0e-ba59-675f69f8392d', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='Mahi Ahdatul Bartish Alati Waqt Hal Hukm.', additional_kwargs={}, response_metadata={}, id='9f4a5dfa-9281-4add-af92-3ec924c3e1a5')], 'chat_history': [{'role': 'user', 'text': "Mahian Musnadat Al Matluba Li Takdeem Ala Parnamesh Tarbiya Til Ma'iz Lim Nisab.", 'lang': 'hi-IN'}, {'role': 'assistant', 'text': 'मेरे पास उपलब्ध आँकड़ों के आधार पर मुझे ज्ञात नहीं है।', 'lang': 'hi-IN'}, {'role': 'user', 'text': 'The Arabic translation of what are the latest schemes launched by the government is ما هي احادة المبادرات', 'lang': 'en-IN'}, {'role': 'assistant', 'text': "The translation you provided is almost correct, but there is a typo. 'احادة' is not a word; it should be 'أحدث' (ahdath) for 'latest'. The correct translation would be: 'ما هي أحدث المبادرات التي أطلقتها الحكومة؟'", 'lang': 'en-IN'}, {'role': 'user', 'text': 'Mahi ahdatul baratish allati waqat hal hukm.', 'lang': 'hi-IN'}]}
// General node data: {'type': 'normal', 'answer': "It seems you are trying to ask a question in Arabic using Roman script. 'Mahi Ahdatul Bartish Alati Waqt Hal Hukm' appears to be a phonetic attempt at asking about the latest initiatives or rulings of the government. Could you please clarify your question or provide it in Arabic script so I can give you an accurate answer?", 'language_code': 'en-IN'}



// message='ما هي أحدث المخططات التي تم إطلاقها؟' thread_id=None input_type='text'
// Traceback (most recent call last):
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\api\chat.py", line 42, in chat
//     result = graph.invoke(
//              ^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\pregel\main.py", line 3884, in invoke
//     for chunk in self.stream(
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\pregel\main.py", line 2938, in stream
//     for _ in runner.tick(
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\pregel\_runner.py", line 207, in tick
//     run_with_retry(
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\pregel\_retry.py", line 617, in run_with_retry
//     return task.proc.invoke(task.input, config)
//            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\_internal\_runnable.py", line 684, in invoke
//     input = context.run(step.invoke, input, config, **kwargs)
//             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\langgraph\_internal\_runnable.py", line 426, in invoke
//     ret = self.func(*args, **kwargs)
//           ^^^^^^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\graph\nodes\translate.py", line 14, in text_input_node
//     result = translate_to_english(
//              ^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\services\sarvam_service.py", line 13, in translate_to_english
//     response = client.text.translate(
//                ^^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\sarvamai\text\client.py", line 177, in translate
//     _response = self._raw_client.translate(
//                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
//   File "C:\Gen AI\Projects\scheme-bot\backend_main\venv\Lib\site-packages\sarvamai\text\raw_client.py", line 214, in translate

//   raise UnprocessableEntityError(
// sarvamai.errors.unprocessable_entity_error.UnprocessableEntityError: headers: {'date': 'Mon, 15 Jun 2026 06:11:05 GMT', 'content-type': 'application/json', 'content-length': '256', 'connection': 'keep-alive', 'server': 'uvicorn', 'x-request-id': '20260615_8e0d5114-a36b-4146-b720-d6ae31019795', 'access-control-allow-origin': '*', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'x-frame-options': 'DENY', 'x-content-type-options': 'nosniff', 'referrer-policy': 'strict-origin-when-cross-origin', 'permissions-policy': 'geolocation=(), camera=(), microphone=(), payment=()', 'content-security-policy': "default-src 'none'; frame-ancestors 'none'", 'cache-control': 'no-store, no-cache, must-revalidate', 'pragma': 'no-cache', 'expires': '0', 'x-xss-protection': '0'}, status_code: 422, body: {'error': {'message': 'Unable to detect the language of the input text, please explicitly pass the `source_language_code` parameter with a supported language.', 'code': 'unprocessable_entity_error', 'request_id': '20260615_8e0d5114-a36b-4146-b720-d6ae31019795'}}
// During task with name 'text_input' and id 'f681c5fd-bee7-7c57-de74-c42e75aea491'
// INFO:     127.0.0.1:53329 - "POST /chat/chat HTTP/1.1" 200 OK