import React from 'react';
import { AbsoluteFill, Audio, Video, Img, useVideoConfig, useCurrentFrame, interpolate, spring, staticFile } from 'remotion';

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

// TIMING CONSTANTS
const INTRO_DURATION_SECONDS = 3;
const OUTRO_DURATION_SECONDS = 4;

// HIGHLIGHT KEYWORDS (these flash in gold)
const HIGHLIGHT_KEYWORDS = [
    'love', 'money', 'wealth', 'success', 'luck', 'fortune', 'danger',
    'warning', 'amazing', 'incredible', 'powerful', 'energy', 'passion',
    'career', 'health', 'relationship', 'surprise', 'unexpected',
    ...Object.keys(ZODIAC_SYMBOLS).map(s => s.toLowerCase())
];

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
    
    // Calculate which background to show based on time
    const totalImages = images?.length || 1;
    const segmentDuration = durationInFrames / totalImages;
    const currentImageIndex = Math.min(Math.floor(frame / segmentDuration), totalImages - 1);
    const currentImage = images?.[currentImageIndex] || "";
    
    // Animated glow intensity
    const glowIntensity = 0.3 + Math.sin(frame * 0.05) * 0.15;
    
    // Color shift for variety
    const hueShift = (frame * 0.1) % 360;
    
    // INTRO/OUTRO TIMING
    const introDurationFrames = INTRO_DURATION_SECONDS * fps;
    const outroDurationFrames = OUTRO_DURATION_SECONDS * fps;
    const outroStartFrame = durationInFrames - outroDurationFrames;
    
    const isIntroPhase = frame < introDurationFrames;
    const isOutroPhase = frame >= outroStartFrame;
    const isMainPhase = !isIntroPhase && !isOutroPhase;
    
    // CAMERA SHAKE - Trigger on highlight keywords (every ~100 frames for variety)
    const shakeIntensity = (frame % 100 < 5) ? 3 : 0;
    const shakeX = shakeIntensity * Math.sin(frame * 0.5);
    const shakeY = shakeIntensity * Math.cos(frame * 0.7);
    
    // COUNTDOWN TIMER
    const remainingSeconds = Math.max(0, Math.ceil((durationInFrames - frame) / fps));
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    return (
        <AbsoluteFill style={{ 
            background: gradient,
            overflow: 'hidden',
            transform: `translate(${shakeX}px, ${shakeY}px)`, // Camera shake
        }}>
            {/* LAYER 0: VIDEO/IMAGE BACKGROUND */}
            {currentImage && (
                <AbsoluteFill style={{ zIndex: 0 }}>
                    <BackgroundClip src={currentImage} index={currentImageIndex} total={totalImages} />
                </AbsoluteFill>
            )}
            
            {/* LAYER 1: GRADIENT OVERLAY (Zodiac Theme) */}
            <AbsoluteFill style={{ 
                zIndex: 1,
                background: gradient,
                opacity: currentImage ? 0.6 : 1, // More transparent if we have a bg video
                mixBlendMode: 'overlay'
            }} />
            
            {/* LAYER 2: ANIMATED COSMIC PARTICLES */}
            <AbsoluteFill style={{ zIndex: 2, pointerEvents: 'none' }}>
                {/* Floating particles effect */}
                {[...Array(25)].map((_, i) => {
                    const x = (i * 137.5) % 100;
                    const y = ((i * 73) + frame * 0.5) % 140;
                    const size = 3 + (i % 4) * 3;
                    const opacity = 0.2 + (i % 5) * 0.12;
                    const delay = i * 0.1;
                    return (
                        <div
                            key={i}
                            style={{
                                position: 'absolute',
                                left: `${x}%`,
                                top: `${y - 40}%`,
                                width: size,
                                height: size,
                                borderRadius: '50%',
                                backgroundColor: 'white',
                                opacity: opacity,
                                boxShadow: `0 0 ${size * 2}px ${size}px rgba(255,255,255,${opacity})`,
                                filter: `blur(${1 + i % 2}px)`,
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
                    fontSize: 500,
                    opacity: 0.08,
                    color: 'white',
                    fontFamily: 'serif',
                    filter: `drop-shadow(0 0 50px rgba(255,255,255,${glowIntensity}))`,
                }}>
                    {symbol}
                </div>
            </AbsoluteFill>
            
            {/* LAYER 3: ANIMATED VIGNETTE */}
            <AbsoluteFill style={{ 
                zIndex: 3,
                background: `radial-gradient(ellipse at center, transparent 20%, rgba(0,0,0,${0.4 + glowIntensity * 0.3}) 80%, rgba(0,0,0,0.9) 100%)`,
                pointerEvents: 'none'
            }} />
            
            {/* LAYER 4: ANIMATED LIGHT BEAMS */}
            <AbsoluteFill style={{ zIndex: 4, pointerEvents: 'none', overflow: 'hidden' }}>
                {[0, 1, 2].map((i) => {
                    const beamX = ((frame * 2 + i * 400) % 1500) - 200;
                    const beamOpacity = 0.08 + Math.sin(frame * 0.03 + i) * 0.04;
                    return (
                        <div
                            key={`beam-${i}`}
                            style={{
                                position: 'absolute',
                                left: beamX,
                                top: -200,
                                width: 150,
                                height: 2500,
                                background: `linear-gradient(180deg, transparent, rgba(255,215,0,${beamOpacity}), transparent)`,
                                transform: 'rotate(25deg)',
                                filter: 'blur(30px)',
                            }}
                        />
                    );
                })}
            </AbsoluteFill>
            
            {/* LAYER 4.5: FLOATING EMOJI REACTIONS */}
            <AbsoluteFill style={{ zIndex: 4, pointerEvents: 'none' }}>
                {['✨', '🔥', '💫', '⭐', '💎'].map((emoji, i) => {
                    const emojiY = ((frame * 1.5 + i * 100) % 2200) - 200;
                    const emojiX = 50 + Math.sin(frame * 0.02 + i * 2) * 400;
                    const emojiOpacity = interpolate(emojiY, [0, 500, 1500, 2000], [0, 0.6, 0.6, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
                    const emojiScale = 0.8 + Math.sin(frame * 0.1 + i) * 0.2;
                    return (
                        <div
                            key={`emoji-${i}`}
                            style={{
                                position: 'absolute',
                                left: emojiX,
                                top: emojiY,
                                fontSize: 40 + i * 10,
                                opacity: emojiOpacity,
                                transform: `scale(${emojiScale}) rotate(${frame * (i % 2 === 0 ? 1 : -1)}deg)`,
                            }}
                        >
                            {emoji}
                        </div>
                    );
                })}
            </AbsoluteFill>
            
            {/* COUNTDOWN TIMER (Top Right Corner) */}
            <div style={{
                position: 'absolute',
                top: 100,
                right: 30,
                zIndex: 20,
                fontFamily: 'Montserrat, monospace',
                fontSize: 24,
                fontWeight: 700,
                color: 'rgba(255,255,255,0.7)',
                background: 'rgba(0,0,0,0.3)',
                padding: '8px 16px',
                borderRadius: 20,
                backdropFilter: 'blur(5px)',
                border: '1px solid rgba(255,255,255,0.2)',
            }}>
                ⏱️ {timeString}
            </div>
            
            {/* ANIMATED SUBSCRIBE BELL (Bottom Right) */}
            {isMainPhase && (
                <div style={{
                    position: 'absolute',
                    bottom: 80,
                    right: 30,
                    zIndex: 20,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 8,
                }}>
                    <div style={{
                        fontSize: 50,
                        transform: `rotate(${Math.sin(frame * 0.1) * 15}deg)`,
                        filter: 'drop-shadow(0 0 10px rgba(255,215,0,0.5))',
                    }}>
                        🔔
                    </div>
                    <div style={{
                        fontFamily: 'Montserrat, sans-serif',
                        fontSize: 14,
                        fontWeight: 700,
                        color: '#FFD700',
                        textTransform: 'uppercase',
                        letterSpacing: 2,
                        opacity: 0.5 + Math.sin(frame * 0.05) * 0.3,
                    }}>
                        Subscribe
                    </div>
                </div>
            )}
            
            {/* ZODIAC SIGN HEADER */}
            <div style={{
                position: 'absolute',
                top: 80,
                left: 0,
                right: 0,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 5,
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
                        fontFamily: 'Montserrat, sans-serif',
                        textTransform: 'uppercase',
                        letterSpacing: 4,
                    }}>{zodiacSign}</span>
                </div>
            </div>

            {/* INTRO HOOK (First 3 seconds) */}
            {isIntroPhase && (
                <IntroHook 
                    zodiacSign={zodiacSign} 
                    symbol={symbol} 
                    frame={frame} 
                    fps={fps} 
                    introDurationFrames={introDurationFrames} 
                />
            )}
            
            {/* OUTRO CTA (Last 4 seconds) */}
            {isOutroPhase && (
                <OutroHook 
                    frame={frame - outroStartFrame} 
                    fps={fps} 
                    symbol={symbol}
                />
            )}

            {/* CAPTION TEXT - MAIN FOCUS (Only during main phase) */}
            {isMainPhase && (
                <AbsoluteFill style={{ 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    zIndex: 10,
                    padding: 40,
                }}>
                    <CaptionsLayer captions={captions} />
                </AbsoluteFill>
            )}
            
            {/* LAYER 11: SCANLINES OVERLAY (Cinematic Film Look) */}
            <AbsoluteFill style={{ 
                zIndex: 11,
                pointerEvents: 'none',
                background: `repeating-linear-gradient(
                    0deg,
                    transparent 0px,
                    rgba(0,0,0,0.03) 1px,
                    transparent 2px,
                    transparent 4px
                )`,
                mixBlendMode: 'multiply'
            }} />
            
            {/* LAYER 12: SUBTLE NOISE (Film Grain Effect) */}
            <AbsoluteFill style={{ 
                zIndex: 12,
                pointerEvents: 'none',
                opacity: 0.05,
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
            }} />
            
            {/* PROGRESS BAR */}
            <div style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: 8,
                backgroundColor: 'rgba(255,255,255,0.2)',
                zIndex: 15,
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
            
            {/* WHOOSH SOUND - At end of intro (frame 80-90 = ~2.7-3 seconds) */}
            {frame >= introDurationFrames - 10 && frame <= introDurationFrames + 5 && (
                <Audio 
                    src={staticFile('/assets/whoosh.mp3')} 
                    startFrom={0}
                    volume={0.5}
                    placeholder={null} 
                    onPointerEnterCapture={undefined} 
                    onPointerLeaveCapture={undefined} 
                />
            )}
            
            {/* SPARKLE SOUND - At start of outro */}
            {frame >= outroStartFrame && frame <= outroStartFrame + 15 && (
                <Audio 
                    src={staticFile('/assets/sparkle.mp3')} 
                    startFrom={0}
                    volume={0.4}
                    placeholder={null} 
                    onPointerEnterCapture={undefined} 
                    onPointerLeaveCapture={undefined} 
                />
            )}
            
            {/* BACKGROUND MUSIC (Lo-Fi) with DUCKING when voice plays */}
            <Audio 
                src={staticFile('/assets/lofi_bg.mp3')} 
                startFrom={0}
                volume={audioSrc ? 0.15 : 0.35} // Duck when voice is playing
                loop
                placeholder={null} 
                onPointerEnterCapture={undefined} 
                onPointerLeaveCapture={undefined} 
            />
            
            {/* BELL SOUND - Short ding at outro start */}
            {frame >= outroStartFrame + 20 && frame <= outroStartFrame + 35 && (
                <Audio 
                    src={staticFile('/assets/bell.mp3')} 
                    startFrom={0}
                    volume={0.3}
                    placeholder={null} 
                    onPointerEnterCapture={undefined} 
                    onPointerLeaveCapture={undefined} 
                />
            )}
        </AbsoluteFill>
    );
};

const BackgroundClip: React.FC<{src: string, index: number, total: number}> = ({ src, index, total }) => {
    const frame = useCurrentFrame();
    
    // Smooth Scale Ken Burns
    const scale = interpolate(frame, [0, 150], [1.0, 1.15], { extrapolateRight: 'clamp' });
    
    // Fallback to a known good image
    const finalSrc = src || "https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg";
    
    // Check if source is strictly a video file to avoid errors
    const isVideo = finalSrc.toLowerCase().endsWith('.mp4');
    
    const style = {
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        transform: `scale(${scale})`
    };

    if (isVideo) {
        // Use staticFile for local assets to prevent timeouts
        // bridge.py downloads these to video-engine/public/assets
        return <Video src={staticFile(src)} style={style} muted loop />;
    }
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return <Img src={finalSrc} style={style} placeholder={undefined} onResize={undefined} onResizeCapture={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} />;
}

// ============================================================
// INTRO HOOK - Animated 3-second splash screen
// ============================================================
const IntroHook: React.FC<{
    zodiacSign: string;
    symbol: string;
    frame: number;
    fps: number;
    introDurationFrames: number;
}> = ({ zodiacSign, symbol, frame, fps, introDurationFrames }) => {
    // Animate scale: zoom in then settle
    const scale = spring({
        frame,
        fps,
        config: { damping: 15, stiffness: 100 }
    });
    
    // Fade in
    const opacity = interpolate(frame, [0, 10], [0, 1]);
    
    // Glow pulse
    const glowPulse = Math.sin(frame * 0.1) * 20 + 40;
    
    // Rotate symbol slightly
    const rotate = Math.sin(frame * 0.05) * 3;
    
    return (
        <AbsoluteFill style={{
            zIndex: 50,
            justifyContent: 'center',
            alignItems: 'center',
            background: 'radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.7) 100%)'
        }}>
            {/* Large Symbol */}
            <div style={{
                fontSize: 250,
                color: 'white',
                transform: `scale(${scale}) rotate(${rotate}deg)`,
                opacity: opacity,
                filter: `drop-shadow(0 0 ${glowPulse}px rgba(255,215,0,0.8))`,
                marginBottom: 40,
            }}>
                {symbol}
            </div>
            
            {/* Title Text */}
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 900,
                fontSize: 55,
                color: 'white',
                textTransform: 'uppercase',
                textAlign: 'center',
                letterSpacing: 6,
                opacity: opacity,
                transform: `translateY(${interpolate(frame, [0, 15], [50, 0], { extrapolateRight: 'clamp' })}px)`,
                textShadow: '0 0 30px rgba(255,215,0,0.5), 0 4px 20px rgba(0,0,0,0.8)',
            }}>
                TODAY'S
            </div>
            
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 900,
                fontSize: 80,
                color: '#FFD700',
                textTransform: 'uppercase',
                textAlign: 'center',
                letterSpacing: 8,
                opacity: opacity,
                transform: `translateY(${interpolate(frame, [5, 20], [50, 0], { extrapolateRight: 'clamp' })}px)`,
                textShadow: '0 0 40px rgba(255,215,0,0.8), 0 4px 20px rgba(0,0,0,0.8)',
                marginTop: 10,
            }}>
                {zodiacSign}
            </div>
            
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 700,
                fontSize: 40,
                color: 'white',
                textTransform: 'uppercase',
                textAlign: 'center',
                letterSpacing: 10,
                opacity: interpolate(frame, [15, 25], [0, 1]),
                marginTop: 20,
                textShadow: '0 4px 20px rgba(0,0,0,0.8)',
            }}>
                HOROSCOPE
            </div>
        </AbsoluteFill>
    );
};

// ============================================================
// OUTRO HOOK - Call-to-action for the last 4 seconds
// ============================================================
const OutroHook: React.FC<{
    frame: number;
    fps: number;
    symbol: string;
}> = ({ frame, fps, symbol }) => {
    const scale = spring({
        frame,
        fps,
        config: { damping: 12, stiffness: 150 }
    });
    
    const opacity = interpolate(frame, [0, 10], [0, 1]);
    const bounce = Math.sin(frame * 0.15) * 5;
    
    return (
        <AbsoluteFill style={{
            zIndex: 50,
            justifyContent: 'center',
            alignItems: 'center',
            background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.8) 100%)'
        }}>
            {/* CTA Text */}
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 900,
                fontSize: 60,
                color: 'white',
                textTransform: 'uppercase',
                textAlign: 'center',
                letterSpacing: 4,
                opacity: opacity,
                transform: `scale(${scale}) translateY(${bounce}px)`,
                textShadow: '0 0 30px rgba(255,215,0,0.5), 0 4px 20px rgba(0,0,0,0.8)',
            }}>
                FOLLOW
            </div>
            
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 700,
                fontSize: 50,
                color: '#FFD700',
                textTransform: 'uppercase',
                textAlign: 'center',
                letterSpacing: 6,
                opacity: opacity,
                marginTop: 10,
                textShadow: '0 0 40px rgba(255,215,0,0.8)',
            }}>
                FOR MORE
            </div>
            
            {/* Animated Symbol */}
            <div style={{
                fontSize: 120,
                color: 'white',
                opacity: interpolate(frame, [20, 30], [0, 1]),
                transform: `rotate(${frame * 2}deg)`,
                marginTop: 40,
                filter: 'drop-shadow(0 0 30px rgba(255,215,0,0.6))',
            }}>
                {symbol}
            </div>
            
            {/* Arrow pointing up (like/follow indicator) */}
            <div style={{
                fontSize: 60,
                color: 'white',
                opacity: interpolate(frame, [30, 40], [0, 1]),
                transform: `translateY(${-bounce * 2}px)`,
                marginTop: 30,
            }}>
                ☝️
            </div>
        </AbsoluteFill>
    );
};

// ============================================================
// CAPTIONS LAYER with Word Highlighting
// ============================================================
const CaptionsLayer: React.FC<{captions: Caption[]}> = ({ captions }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const currentTime = frame / fps;

    if (!captions || captions.length === 0) {
        return (
            <div style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 700,
                fontSize: 60,
                color: 'white',
                textAlign: 'center',
                textShadow: '0 4px 10px rgba(0,0,0,0.5)',
            }}>
                Wait...
                <div style={{fontSize: 30, fontWeight: 400}}>Checking Stars...</div>
            </div>
        );
    }

    const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);

    if (!activeCaption) {
        return null;
    }
    
    const captionStartFrame = activeCaption.start * fps;
    const timeInCaption = frame - captionStartFrame;
    
    const opacity = interpolate(timeInCaption, [0, 5], [0, 1]);
    const translateY = interpolate(timeInCaption, [0, 10], [50, 0], { extrapolateRight: 'clamp' });
    
    // Split text into words for highlighting
    const words = activeCaption.text.split(' ');
    
    return (
        <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: `translate(-50%, -50%) translateY(${translateY}px)`,
            width: '85%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 15,
            opacity: opacity
        }}>
            {words.map((word, i) => {
                const isHighlight = HIGHLIGHT_KEYWORDS.some(kw => 
                    word.toLowerCase().replace(/[^a-z]/g, '').includes(kw)
                );
                
                // Animate individual word with slight delay
                const wordDelay = i * 2;
                const wordScale = interpolate(timeInCaption, [wordDelay, wordDelay + 5], [0.8, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
                const wordOpacity = interpolate(timeInCaption, [wordDelay, wordDelay + 3], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
                
                // Gold flash for highlight words
                const goldPulse = isHighlight ? Math.sin((timeInCaption + i) * 0.2) * 0.3 + 0.7 : 0;
                
                return (
                    <span 
                        key={i}
                        style={{
                            fontFamily: 'Montserrat, Poppins, sans-serif',
                            fontWeight: 800,
                            fontSize: isHighlight ? 75 : 70,
                            color: isHighlight ? `rgba(255, 215, 0, ${0.7 + goldPulse})` : 'white',
                            textTransform: 'uppercase',
                            textAlign: 'center',
                            lineHeight: 1.2,
                            textShadow: isHighlight 
                                ? `0 0 ${20 + goldPulse * 30}px rgba(255,215,0,0.8), 0 10px 30px rgba(0,0,0,0.8)`
                                : '0 10px 30px rgba(0,0,0,0.8)',
                            letterSpacing: 1,
                            transform: `scale(${wordScale})`,
                            opacity: wordOpacity,
                            display: 'inline-block',
                            position: 'relative',
                        }}
                    >
                        {word}
                        {/* PARTICLE BURST for highlighted words */}
                        {isHighlight && timeInCaption > wordDelay && timeInCaption < wordDelay + 20 && (
                            <>
                                {[0,1,2,3,4,5,6,7].map((p) => {
                                    const angle = (p / 8) * Math.PI * 2;
                                    const distance = (timeInCaption - wordDelay) * 4;
                                    const particleX = Math.cos(angle) * distance;
                                    const particleY = Math.sin(angle) * distance; 
                                    const particleOpacity = interpolate(timeInCaption - wordDelay, [0, 5, 15, 20], [0, 1, 1, 0], { extrapolateRight: 'clamp' });
                                    return (
                                        <span
                                            key={`particle-${p}`}
                                            style={{
                                                position: 'absolute',
                                                left: '50%',
                                                top: '50%',
                                                transform: `translate(-50%, -50%) translate(${particleX}px, ${particleY}px)`,
                                                fontSize: 16,
                                                opacity: particleOpacity,
                                                pointerEvents: 'none',
                                            }}
                                        >
                                            ✨
                                        </span>
                                    );
                                })}
                            </>
                        )}
                    </span>
                );
            })}
        </div>
    );
};
