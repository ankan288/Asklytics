'use client';

import { useEffect, useRef, useState, useMemo, useCallback } from 'react';

interface TextTypeProps {
  className?: string;
  showCursor?: boolean;
  cursorCharacter?: string;
  text: string | string[];
  typingSpeed?: number;
  pauseDuration?: number;
  deletingSpeed?: number;
  loop?: boolean;
  textColors?: string[];
  variableSpeed?: { min: number; max: number };
}

const TextType = ({
  text,
  typingSpeed = 50,
  pauseDuration = 2000,
  deletingSpeed = 30,
  loop = true,
  className = '',
  showCursor = true,
  cursorCharacter = '|',
  textColors = [],
  variableSpeed,
}: TextTypeProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const cursorRef = useRef<HTMLSpanElement>(null);

  const textArray = useMemo(() => (Array.isArray(text) ? text : [text]), [text]);

  const getRandomSpeed = useCallback(() => {
    if (!variableSpeed) return typingSpeed;
    const { min, max } = variableSpeed;
    return Math.random() * (max - min) + min;
  }, [variableSpeed, typingSpeed]);

  const currentColor = textColors.length > 0
    ? textColors[currentTextIndex % textColors.length]
    : 'inherit';

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    const currentText = textArray[currentTextIndex];

    if (isDeleting) {
      if (displayedText === '') {
        setIsDeleting(false);
        if (currentTextIndex === textArray.length - 1 && !loop) return;
        setCurrentTextIndex(prev => (prev + 1) % textArray.length);
        setCurrentCharIndex(0);
        timeout = setTimeout(() => {}, pauseDuration);
      } else {
        timeout = setTimeout(() => {
          setDisplayedText(prev => prev.slice(0, -1));
        }, deletingSpeed);
      }
    } else {
      if (currentCharIndex < currentText.length) {
        timeout = setTimeout(() => {
          setDisplayedText(prev => prev + currentText[currentCharIndex]);
          setCurrentCharIndex(prev => prev + 1);
        }, variableSpeed ? getRandomSpeed() : typingSpeed);
      } else if (textArray.length >= 1) {
        if (!loop && currentTextIndex === textArray.length - 1) return;
        timeout = setTimeout(() => {
          setIsDeleting(true);
        }, pauseDuration);
      }
    }

    return () => clearTimeout(timeout);
  }, [
    currentCharIndex, displayedText, isDeleting, typingSpeed,
    deletingSpeed, pauseDuration, textArray, currentTextIndex,
    loop, variableSpeed, getRandomSpeed,
  ]);

  return (
    <span className={className} style={{ display: 'inline-block', whiteSpace: 'pre-wrap' }}>
      <span style={{ color: currentColor }}>{displayedText}</span>
      {showCursor && (
        <span
          ref={cursorRef}
          style={{
            marginLeft: '2px',
            display: 'inline-block',
            animation: 'texttype-blink 1s step-end infinite',
          }}
        >
          {cursorCharacter}
          <style>{`@keyframes texttype-blink { 0%,100%{opacity:1} 50%{opacity:0} }`}</style>
        </span>
      )}
    </span>
  );
};

export default TextType;
