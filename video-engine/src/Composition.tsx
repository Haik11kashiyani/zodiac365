import React from 'react';
import { AbsoluteFill, Audio, useVideoConfig, useCurrentFrame, interpolate, spring, staticFile } from 'remotion';

interface Caption {
    start: number;
    end: number;
    text: string;
}

interface ZodiacCompositionProps {
    scriptText: string;
    audioSrc: string;
    captions: Caption[];
    images: string[];
    title?: string;
}

// Zodiac gradient backgrounds based on element
const ZODIAC_GRADIENTS: Record<string, string> = {
    // Fire Signs - Warm reds/oranges
    'Aries': 'linear-gradient(135deg, #ff6b35 0%, #f7c59f 50%, #cc3300 100%)',
    'Leo': 'linear-gradient(135deg, #ffd700 0%, #ff8c00 50%, #ff4500 100%)',
    'Sagittarius': 'linear-gradient(135deg, #9b4dca 0%, #ff6b6b 50%, #ffa500 100%)',
    
    // Earth Signs - Greens/Browns
    'Taurus': 'linear-gradient(135deg, #228b22 0%, #90ee90 50%, #2e8b57 100%)',
    'Virgo': 'linear-gradient(135deg, #8fbc8f 0%, #f5f5dc 50%, #6b8e23 100%)',
    'Capricorn': 'linear-gradient(135deg, #4a4a4a 0%, #8b4513 50%, #2f2f2f 100%)',
    
    // Air Signs - Blues/Whites
    'Gemini': 'linear-gradient(135deg, #87ceeb 0%, #e6e6fa 50%, #4169e1 100%)',
    'Libra': 'linear-gradient(135deg, #ffb6c1 0%, #e6e6fa 50%, #dda0dd 100%)',
    'Aquarius': 'linear-gradient(135deg, #00bfff 0%, #1e90ff 50%, #000080 100%)',
    
    // Water Signs - Deep blues/purples
    'Cancer': 'linear-gradient(135deg, #c0c0c0 0%, #87ceeb 50%, #4682b4 100%)',
    'Scorpio': 'linear-gradient(135deg, #800000 0%, #4a0080 50%, #000000 100%)',
    'Pisces': 'linear-gradient(135deg, #40e0d0 0%, #9370db 50%, #483d8b 100%)',
};

const ZODIAC_SYMBOLS: Record<string, string> = {
    'Aries': '♈',
    'Taurus': '♉',
    'Gemini': '♊',
    'Cancer': '♋',
    'Leo': '♌',
    'Virgo': '♍',
    'Libra': '♎',
    'Scorpio': '♏',
    'Sagittarius': '♐',
    'Capricorn': '♑',
    'Aquarius': '♒',
    'Pisces': '♓',
};

export const ZodiacComposition: React.FC<ZodiacCompositionProps> = ({ 
    scriptText, 
    audioSrc, 
    captions, 
    images,
    title = ''
}) => {
    const frame = useCurrentFrame(); 
    const { fps, durationInFrames, width, height } = useVideoConfig();
    
    // Extract zodiac sign from title or default to Aries
    const zodiacSign = Object.keys(ZODIAC_GRADIENTS).find(sign => 
        title?.toLowerCase().includes(sign.toLowerCase())
    ) || 'Aries';
    
    const gradient = ZODIAC_GRADIENTS[zodiacSign];
    const symbol = ZODIAC_SYMBOLS[zodiacSign];
    
    // Animated background pulse
    const pulse = Math.sin(frame * 0.02) * 0.1 + 1;
    
    // Progress bar
    const progress = (frame / durationInFrames) * 100;

    return (
        <AbsoluteFill style={{ 
            background: gradient,
            overflow: 'hidden'
        }}>
            {/* ANIMATED COSMIC BACKGROUND */}
            <AbsoluteFill style={{ zIndex: 0 }}>
                {/* Floating particles effect */}
                {[...Array(15)].map((_, i) => {
                    const x = (i * 137.5) % 100;
                    const y = ((i * 73) + frame * 0.3) % 120;
                    const size = 4 + (i % 3) * 2;
                    const opacity = 0.3 + (i % 5) * 0.1;
                    return (
                        <div
                            key={i}
                            style={{
                                position: 'absolute',
                                left: `${x}%`,
                                top: `${y - 20}%`,
                                width: size,
                                height: size,
                                borderRadius: '50%',
                                backgroundColor: 'white',
                                opacity: opacity,
                                boxShadow: '0 0 10px white',
                            }}
                        />
                    );
                })}
                
                {/* Large zodiac symbol in background */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: `translate(-50%, -50%) scale(${pulse})`,
                    fontSize: 400,
                    opacity: 0.1,
                    color: 'white',
                    fontFamily: 'serif',
                }}>
                    {symbol}
                </div>
            </AbsoluteFill>
            
            {/* DARK OVERLAY FOR READABILITY */}
            <AbsoluteFill style={{ 
                zIndex: 1,
                background: 'radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.6) 100%)'
            }} />
            
            {/* ZODIAC SIGN HEADER */}
            <div style={{
                position: 'absolute',
                top: 80,
                left: 0,
                right: 0,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 2,
            }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 20,
                    padding: '15px 40px',
                    background: 'rgba(0,0,0,0.4)',
                    borderRadius: 50,
                    backdropFilter: 'blur(10px)',
                }}>
                    <span style={{ 
                        fontSize: 60, 
                        color: 'white',
                        textShadow: '0 0 20px rgba(255,255,255,0.5)'
                    }}>{symbol}</span>
                    <span style={{
                        fontSize: 48,
                        fontWeight: 900,
                        color: 'white',
                        fontFamily: 'Arial Black, sans-serif',
                        textTransform: 'uppercase',
                        letterSpacing: 4,
                    }}>{zodiacSign}</span>
                </div>
            </div>

            {/* CAPTION TEXT - MAIN FOCUS */}
            <AbsoluteFill style={{ 
                justifyContent: 'center', 
                alignItems: 'center',
                zIndex: 3,
                padding: 40,
            }}>
                <CaptionsLayer captions={captions} />
            </AbsoluteFill>
            
            {/* PROGRESS BAR */}
            <div style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: 8,
                backgroundColor: 'rgba(255,255,255,0.2)',
                zIndex: 4,
            }}>
                <div style={{
                    width: `${progress}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #FFD700, #FFA500)',
                    boxShadow: '0 0 20px #FFD700, 0 0 40px #FFA500',
                    transition: 'width 0.1s linear',
                }} />
            </div>

            {/* AUDIO */}
            {audioSrc && (
                <Audio 
                    src={staticFile(audioSrc)} 
                    placeholder={null} 
                    onPointerEnterCapture={undefined} 
                    onPointerLeaveCapture={undefined} 
                />
            )}
        </AbsoluteFill>
    );
};

const CaptionsLayer: React.FC<{captions: Caption[]}> = ({ captions }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const currentTime = frame / fps;

    // Debug: Check if captions exist
    if (!captions || captions.length === 0) {
        return (
            <div style={{
                fontFamily: 'Arial Black, Impact, sans-serif',
                fontWeight: 900,
                fontSize: 60,
                color: 'white',
                textAlign: 'center',
                textShadow: '4px 4px 0px #000, -4px -4px 0px #000',
            }}>
                Loading...
            </div>
        );
    }

    const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);

    if (!activeCaption) {
        // Show nothing between captions (normal behavior)
        return null;
    }
    
    // Calculate local frame for the caption to animate entry
    const captionStartFrame = activeCaption.start * fps;
    const timeInCaption = frame - captionStartFrame;
    
    // Pop-in spring animation
    const scale = spring({
        frame: timeInCaption,
        fps,
        config: { damping: 12, stiffness: 200 }
    });
    
    // Slight bounce/wiggle for energy
    const wiggle = Math.sin(timeInCaption * 0.15) * 1.5;

    return (
        <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: `translate(-50%, -50%) scale(${scale}) rotate(${wiggle}deg)`,
            width: '90%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
        }}>
            <div style={{
                fontFamily: 'Arial Black, Impact, sans-serif',
                fontWeight: 900,
                fontSize: 100,
                color: 'white',
                textTransform: 'uppercase',
                textAlign: 'center',
                lineHeight: 1.1,
                // Heavy text shadow for maximum contrast
                textShadow: `
                    5px 5px 0px #000,
                    -5px -5px 0px #000,
                    5px -5px 0px #000,
                    -5px 5px 0px #000,
                    0 0 40px rgba(0,0,0,0.9)
                `,
                WebkitTextStroke: '3px black',
                letterSpacing: 3,
            }}>
                {activeCaption.text}
            </div>
        </div>
    );
};
