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

    return (
        <AbsoluteFill style={{ 
            background: gradient,
            overflow: 'hidden'
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

            {/* CAPTION TEXT - MAIN FOCUS */}
            <AbsoluteFill style={{ 
                justifyContent: 'center', 
                alignItems: 'center',
                zIndex: 10,
                padding: 40,
            }}>
                <CaptionsLayer captions={captions} />
            </AbsoluteFill>
            
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

const CaptionsLayer: React.FC<{captions: Caption[]}> = ({ captions }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const currentTime = frame / fps;

    // Debug: Check if captions exist
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
    
    // Calculate local frame for the caption to animate entry
    const captionStartFrame = activeCaption.start * fps;
    const timeInCaption = frame - captionStartFrame;
    
    // Animating slide up + fade in
    const opacity = interpolate(timeInCaption, [0, 5], [0, 1]);
    const translateY = interpolate(timeInCaption, [0, 10], [50, 0], { extrapolateRight: 'clamp' });
    
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
            opacity: opacity
        }}>
            <div style={{
                fontFamily: 'Montserrat, Poppins, sans-serif',
                fontWeight: 800,
                fontSize: 70, // Slightly smaller for multi-line support
                color: 'white',
                textTransform: 'uppercase',
                textAlign: 'center',
                lineHeight: 1.2,
                // Elegant soft shadow + stroke
                textShadow: '0 10px 30px rgba(0,0,0,0.8)',
                letterSpacing: 1,
            }}>
                {activeCaption.text}
            </div>
        </div>
    );
};
