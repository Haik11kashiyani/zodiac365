import React from 'react';
import { AbsoluteFill, Audio, Video, Img, useVideoConfig, useCurrentFrame, interpolate, spring, staticFile } from 'remotion';

interface Caption {
    start: number;
    end: number;
    text: string;
}

// Asset type definition - supports legacy string or new sequence object
type AssetSpec = string | { type: 'sequence', prefix: string, count: number };

interface ZodiacCompositionProps {
    scriptText: string;
    audioSrc: string;
    captions: Caption[];
    images: AssetSpec[];
    title?: string;
    durationInFrames?: number;
    optimizeForCI?: boolean;
    // NEW PROPS
    luckyNumbers?: string[];
    luckyColor?: string;
    monthlyVibe?: string;
    date?: string;
    predictionType?: string;
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

// CONSTELLATION STAR PATTERNS (x%, y% coordinates)
// Each constellation is simplified to key stars with connections
const ZODIAC_CONSTELLATIONS: Record<string, {stars: [number, number][], connections: [number, number][]}> = {
    'Aries': {
        stars: [[30, 35], [40, 30], [55, 28], [70, 32]],
        connections: [[0,1], [1,2], [2,3]]
    },
    'Taurus': {
        stars: [[25, 40], [35, 35], [45, 30], [55, 35], [65, 32], [50, 45], [60, 48]],
        connections: [[0,1], [1,2], [2,3], [3,4], [2,5], [5,6]]
    },
    'Gemini': {
        stars: [[30, 25], [35, 40], [40, 55], [55, 25], [60, 40], [65, 55]],
        connections: [[0,1], [1,2], [3,4], [4,5], [1,4]]
    },
    'Cancer': {
        stars: [[35, 35], [45, 30], [55, 35], [45, 45], [50, 50]],
        connections: [[0,1], [1,2], [1,3], [3,4]]
    },
    'Leo': {
        stars: [[25, 35], [35, 25], [50, 28], [60, 35], [55, 50], [45, 55], [35, 50]],
        connections: [[0,1], [1,2], [2,3], [3,4], [4,5], [5,6], [6,0]]
    },
    'Virgo': {
        stars: [[25, 30], [35, 35], [45, 32], [55, 28], [50, 45], [60, 50], [40, 55]],
        connections: [[0,1], [1,2], [2,3], [2,4], [4,5], [4,6]]
    },
    'Libra': {
        stars: [[30, 40], [45, 30], [60, 40], [35, 55], [55, 55]],
        connections: [[0,1], [1,2], [0,3], [2,4]]
    },
    'Scorpio': {
        stars: [[20, 35], [30, 30], [40, 32], [50, 35], [55, 45], [60, 55], [65, 50], [70, 45]],
        connections: [[0,1], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7]]
    },
    'Sagittarius': {
        stars: [[30, 50], [40, 40], [50, 35], [60, 30], [55, 45], [65, 50]],
        connections: [[0,1], [1,2], [2,3], [2,4], [4,5]]
    },
    'Capricorn': {
        stars: [[25, 35], [35, 28], [50, 30], [60, 38], [55, 50], [40, 55]],
        connections: [[0,1], [1,2], [2,3], [3,4], [4,5], [5,0]]
    },
    'Aquarius': {
        stars: [[25, 30], [35, 35], [45, 32], [55, 38], [65, 35], [50, 50], [60, 55]],
        connections: [[0,1], [1,2], [2,3], [3,4], [3,5], [5,6]]
    },
    'Pisces': {
        stars: [[20, 40], [30, 35], [40, 38], [50, 35], [60, 32], [45, 50], [55, 55]],
        connections: [[0,1], [1,2], [2,3], [3,4], [2,5], [5,6]]
    }
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

// SURPRISE KEYWORDS (trigger screen flash)
const SURPRISE_KEYWORDS = [
    'surprise', 'unexpected', 'shocking', 'amazing', 'incredible', 'wow',
    'suddenly', 'alert', 'breaking', 'major', 'big', 'huge', 'explosive'
];

// WARNING KEYWORDS (trigger dark pulse + bass visual)
const WARNING_KEYWORDS = [
    'danger', 'warning', 'caution', 'careful', 'beware', 'risk',
    'threat', 'problem', 'avoid', 'negative', 'bad', 'dark', 'difficult'
];

// UNDERLINE KEYWORDS (animated underline effect)
const UNDERLINE_KEYWORDS = [
    'today', 'tomorrow', 'week', 'month', 'year', 'important', 'key',
    'must', 'need', 'should', 'will', 'destiny', 'fate', 'future', 'path'
];

// POSITIVE KEYWORDS (confetti burst + celebration)
const POSITIVE_KEYWORDS = [
    'love', 'success', 'fortune', 'luck', 'blessing', 'joy', 'happiness',
    'prosperity', 'wealth', 'win', 'victory', 'celebrate', 'amazing', 'wonderful',
    'excellent', 'great', 'fantastic', 'brilliant', 'perfect', 'best'
];

// REVEAL KEYWORDS (slow motion effect)
const REVEAL_KEYWORDS = [
    'reveal', 'secret', 'hidden', 'discover', 'truth', 'mystery', 'unveil',
    'special', 'unique', 'rare', 'exclusive', 'finally', 'moment', 'now'
];

// EMOTION -> AURA COLOR MAPPING
const EMOTION_AURA_COLORS: Record<string, string> = {
    'love': '#FF69B4',      // Pink
    'passion': '#FF1493',   // Deep Pink
    'success': '#FFD700',   // Gold
    'wealth': '#FFD700',    // Gold
    'money': '#00FF00',     // Green
    'danger': '#FF0000',    // Red
    'warning': '#FF4500',   // Orange Red
    'peace': '#87CEEB',     // Sky Blue
    'calm': '#ADD8E6',      // Light Blue
    'energy': '#FF8C00',    // Dark Orange
    'power': '#8B00FF',     // Violet
};

export const ZodiacComposition: React.FC<ZodiacCompositionProps> = ({ 
    scriptText, 
    audioSrc, 
    captions, 
    images,
    title = '',
    optimizeForCI = false,
    luckyNumbers = [],
    luckyColor = '',
    monthlyVibe = '',
    date = '',
    predictionType = 'DAILY',
}) => {
    const frame = useCurrentFrame(); 
    const { fps, width, height } = useVideoConfig(); // durationInFrames is obtained from props or config
    const durationInFrames = useVideoConfig().durationInFrames;
    
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
    
    // GLITCH EFFECT - Trigger at scene transitions
    const frameInSegment = frame % segmentDuration;
    const isTransitioning = frameInSegment < 8 || frameInSegment > segmentDuration - 8;
    // OPTIMIZATION: Disable glitch in CI
    const glitchIntensity = (isTransitioning && !optimizeForCI) ? Math.random() * 15 : 0;
    const rgbSplitX = (isTransitioning && !optimizeForCI) ? Math.sin(frame * 2) * 8 : 0;
    const rgbSplitY = (isTransitioning && !optimizeForCI) ? Math.cos(frame * 3) * 4 : 0;
    
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
    
    // SCRIPT-AWARE EMOTION DETECTION
    const currentTime = frame / fps;
    const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);
    const currentText = activeCaption?.text?.toLowerCase() || '';
    
    // Detect if current caption has surprise keywords
    const hasSurprise = SURPRISE_KEYWORDS.some(kw => currentText.includes(kw));
    const hasWarning = WARNING_KEYWORDS.some(kw => currentText.includes(kw));
    
    // Screen flash intensity (for surprise moments)
    const flashOpacity = hasSurprise ? 
        interpolate(frame % 15, [0, 5, 10, 15], [0, 0.4, 0.2, 0], { extrapolateRight: 'clamp' }) : 0;
    
    // Dark pulse for warnings
    const darkPulseOpacity = hasWarning ?
        0.2 + Math.sin(frame * 0.15) * 0.15 : 0;
    
    // Enhanced camera shake for emotion moments
    const emotionShake = (hasSurprise || hasWarning) ? 5 : 0;
    const totalShakeX = shakeX + emotionShake * Math.sin(frame * 0.8);
    const totalShakeY = shakeY + emotionShake * Math.cos(frame * 1.1);
    
    // POSITIVE DETECTION (confetti burst)
    const hasPositive = POSITIVE_KEYWORDS.some(kw => currentText.includes(kw));
    
    // REVEAL DETECTION (slow motion feel - achieved with scale zoom)
    const hasReveal = REVEAL_KEYWORDS.some(kw => currentText.includes(kw));
    const revealZoom = hasReveal ? 1.02 + Math.sin(frame * 0.05) * 0.01 : 1;
    
    // AURA COLOR DETECTION (find first matching emotion word)
    const detectedEmotion = Object.keys(EMOTION_AURA_COLORS).find(emotion => currentText.includes(emotion));
    const auraColor = detectedEmotion ? EMOTION_AURA_COLORS[detectedEmotion] : null;
    // OPTIMIZATION: Disable aura in CI
    const auraOpacity = (auraColor && !optimizeForCI) ? 0.15 + Math.sin(frame * 0.08) * 0.1 : 0;

    // OPTIMIZATION SETTINGS
    const particleCount = optimizeForCI ? 5 : 20; 
    const enableBlur = false;            // DISABLED as requested
    const enableShadows = true;          // ENABLED as requested ("add complex glowing shadows")
    const enableNoise = true;            // RE-ENABLED as requested ("Film Grain add this")
    const starGlowMultiplier = optimizeForCI ? 0 : 0.8;

    return (
        <AbsoluteFill style={{ 
            background: gradient,
            overflow: 'hidden',
            transform: `translate(${totalShakeX}px, ${totalShakeY}px)`, // Enhanced camera shake
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
            
            {/* LAYER 1.5: ANIMATED CONSTELLATION */}
            <AbsoluteFill style={{ zIndex: 1, pointerEvents: 'none' }}>
                {(() => {
                    const constellation = ZODIAC_CONSTELLATIONS[zodiacSign] || ZODIAC_CONSTELLATIONS['Aries'];
                    const { stars, connections } = constellation;
                    
                    // Subtle drift animation
                    const driftX = Math.sin(frame * 0.01) * 2;
                    const driftY = Math.cos(frame * 0.008) * 2;
                    
                    return (
                        <div style={{ 
                            position: 'relative', 
                            width: '100%', 
                            height: '100%',
                            transform: `translate(${driftX}px, ${driftY}px)`,
                        }}>
                            {/* CONNECTING LINES */}
                            <svg style={{ 
                                position: 'absolute', 
                                width: '100%', 
                                height: '100%',
                                opacity: 0.3 + Math.sin(frame * 0.02) * 0.1,
                            }}>
                                {connections.map(([from, to], idx) => {
                                    const lineProgress = interpolate(frame, [idx * 10, idx * 10 + 30], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
                                    const x1 = stars[from][0];
                                    const y1 = stars[from][1];
                                    const x2 = stars[to][0];
                                    const y2 = stars[to][1];
                                    const currentX2 = x1 + (x2 - x1) * lineProgress;
                                    const currentY2 = y1 + (y2 - y1) * lineProgress;
                                    
                                    return (
                                        <line
                                            key={`line-${idx}`}
                                            x1={`${x1}%`}
                                            y1={`${y1}%`}
                                            x2={`${currentX2}%`}
                                            y2={`${currentY2}%`}
                                            stroke="rgba(255,255,255,0.5)"
                                            strokeWidth={2}
                                            strokeLinecap="round"
                                            style={{ filter: enableBlur ? 'drop-shadow(0 0 5px rgba(255,255,255,0.5))' : 'none' }}
                                        />
                                    );
                                })}
                            </svg>
                            
                            {/* STARS */}
                            {stars.map(([x, y], idx) => {
                                const starDelay = idx * 8;
                                const starOpacity = interpolate(frame, [starDelay, starDelay + 15], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
                                const starScale = 1 + Math.sin(frame * 0.05 + idx) * 0.2;
                                const starGlow = 8 + Math.sin(frame * 0.03 + idx * 2) * 4;
                                
                                return (
                                    <div
                                        key={`star-${idx}`}
                                        style={{
                                            position: 'absolute',
                                            left: `${x}%`,
                                            top: `${y}%`,
                                            width: 12,
                                            height: 12,
                                            marginLeft: -6,
                                            marginTop: -6,
                                            borderRadius: '50%',
                                            backgroundColor: 'white',
                                            opacity: starOpacity * 0.8,
                                            transform: `scale(${starScale})`,
                                            boxShadow: enableShadows ? `0 0 ${starGlow}px ${starGlow/2}px rgba(255,255,255,0.8), 0 0 ${starGlow*2}px rgba(255,215,0,0.4)` : 'none',
                                        }}
                                    />
                                );
                            })}
                        </div>
                    );
                })()}
            </AbsoluteFill>
            
            {/* LAYER 2: ANIMATED COSMIC PARTICLES */}
            <AbsoluteFill style={{ zIndex: 2, pointerEvents: 'none' }}>
                {/* Floating particles effect */}
                {[...Array(particleCount)].map((_, i) => {
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
                                boxShadow: enableShadows ? `0 0 ${size * 2}px ${size}px rgba(255,255,255,${opacity})` : 'none',
                                filter: enableBlur ? `blur(${1 + i % 2}px)` : 'none',
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
                    filter: enableBlur ? `drop-shadow(0 0 50px rgba(255,255,255,${glowIntensity}))` : 'none',
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
                                filter: enableBlur ? 'blur(30px)' : 'none',
                            }}
                        />
                    );
                })}
            </AbsoluteFill>
            
            {/* LAYER 4.5: FLOATING EMOJI REACTIONS - REMOVED PER USER REQUEST */}
            {/* 
            <AbsoluteFill style={{ zIndex: 4, pointerEvents: 'none' }}>
                REMOVED
            </AbsoluteFill> 
            */}
            
            {/* ZODIAC WHEEL SPINNER (Bottom Left) */}
            <div style={{
                position: 'absolute',
                bottom: 100,
                left: 30,
                zIndex: 20,
                width: 100,
                height: 100,
            }}>
                <div style={{
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    background: 'rgba(0,0,0,0.4)',
                    border: '2px solid rgba(255,215,0,0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    transform: `rotate(${frame * 0.5}deg)`,
                    boxShadow: '0 0 20px rgba(255,215,0,0.3)',
                }}>
                    {/* All 12 zodiac symbols arranged in circle */}
                    {Object.entries(ZODIAC_SYMBOLS).map(([sign, sym], i) => {
                        const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
                        const radius = 35;
                        const x = Math.cos(angle) * radius;
                        const y = Math.sin(angle) * radius;
                        const isCurrentSign = sign === zodiacSign;
                        
                        return (
                            <div
                                key={sign}
                                style={{
                                    position: 'absolute',
                                    left: `calc(50% + ${x}px)`,
                                    top: `calc(50% + ${y}px)`,
                                    transform: `translate(-50%, -50%) rotate(${-frame * 0.5}deg)`, // Counter-rotate to stay upright
                                    fontSize: isCurrentSign ? 18 : 12,
                                    color: isCurrentSign ? '#FFD700' : 'rgba(255,255,255,0.6)',
                                    fontWeight: isCurrentSign ? 'bold' : 'normal',
                                    filter: isCurrentSign ? 'drop-shadow(0 0 5px #FFD700)' : 'none',
                                    transition: 'all 0.3s ease',
                                }}
                            >
                                {sym}
                            </div>
                        );
                    })}
                    {/* Center current sign */}
                    <div style={{
                        fontSize: 28,
                        color: '#FFD700',
                        filter: 'drop-shadow(0 0 10px rgba(255,215,0,0.8))',
                        transform: `rotate(${-frame * 0.5}deg)`, // Counter-rotate
                    }}>
                        {symbol}
                    </div>
                </div>
            </div>
            
            {/* GLITCH EFFECT OVERLAY (Scene Transitions) */}
            {isTransitioning && (
                <AbsoluteFill style={{
                    zIndex: 30,
                    pointerEvents: 'none',
                    mixBlendMode: 'screen',
                }}>
                    {/* RGB Split - Red Channel */}
                    <AbsoluteFill style={{
                        background: 'rgba(255,0,0,0.1)',
                        transform: `translate(${rgbSplitX}px, ${rgbSplitY}px)`,
                        mixBlendMode: 'multiply',
                    }} />
                    {/* RGB Split - Blue Channel */}
                    <AbsoluteFill style={{
                        background: 'rgba(0,0,255,0.1)',
                        transform: `translate(${-rgbSplitX}px, ${-rgbSplitY}px)`,
                        mixBlendMode: 'multiply',
                    }} />
                    {/* Scanline Glitch */}
                    <AbsoluteFill style={{
                        background: `repeating-linear-gradient(
                            0deg,
                            transparent 0px,
                            rgba(255,255,255,${glitchIntensity * 0.01}) 2px,
                            transparent 4px
                        )`,
                    }} />
                    {/* Random Horizontal Slice */}
                    <div style={{
                        position: 'absolute',
                        left: 0,
                        right: 0,
                        top: `${(frame * 7) % 100}%`,
                        height: 20 + glitchIntensity,
                        background: 'rgba(255,255,255,0.1)',
                        transform: `translateX(${glitchIntensity * (Math.random() > 0.5 ? 1 : -1)}px)`,
                    }} />
                </AbsoluteFill>
            )}
            
            {/* CONFETTI BURST (Positive Moments) */}
            {hasPositive && (
                <AbsoluteFill style={{ zIndex: 28, pointerEvents: 'none' }}>
                    {[...Array(30)].map((_, i) => {
                        const confettiColors = ['#FFD700', '#FF69B4', '#00FF00', '#FF4500', '#00BFFF', '#FF1493', '#7FFF00'];
                        const color = confettiColors[i % confettiColors.length];
                        const startX = 50 + (Math.sin(i * 1.3) * 40);
                        const startY = -10;
                        const fallSpeed = 3 + (i % 5);
                        const sway = Math.sin(frame * 0.1 + i) * 20;
                        const currentY = (frame * fallSpeed + i * 30) % 1300 - 100;
                        const rotation = frame * (2 + i % 4);
                        
                        return (
                            <div
                                key={`confetti-${i}`}
                                style={{
                                    position: 'absolute',
                                    left: `calc(${startX}% + ${sway}px)`,
                                    top: currentY,
                                    width: 10 + (i % 5) * 3,
                                    height: 10 + (i % 3) * 3,
                                    backgroundColor: color,
                                    borderRadius: i % 3 === 0 ? '50%' : '2px',
                                    transform: `rotate(${rotation}deg)`,
                                    opacity: 0.8,
                                    boxShadow: `0 0 5px ${color}`,
                                }}
                            />
                        );
                    })}
                </AbsoluteFill>
            )}
            
            {/* AURA GLOW (Emotion-based color) */}
            {auraColor && (
                <AbsoluteFill style={{
                    zIndex: 27,
                    pointerEvents: 'none',
                    background: `radial-gradient(ellipse at center, ${auraColor}40 0%, ${auraColor}20 40%, transparent 70%)`,
                    opacity: auraOpacity,
                    mixBlendMode: 'screen',
                }} />
            )}
            
            {/* REVEAL ZOOM EFFECT (Slow-mo feel) */}
            {hasReveal && (
                <AbsoluteFill style={{
                    zIndex: 26,
                    pointerEvents: 'none',
                    transform: `scale(${revealZoom})`,
                    background: `radial-gradient(circle at center, transparent 50%, rgba(255,255,255,0.1) 100%)`,
                    boxShadow: 'inset 0 0 100px rgba(255,215,0,0.2)',
                }} />
            )}
            
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
            
            {/* Aggregating captions to show ~3 lines of text (Paragraph View) */}
            {isMainPhase && (
                <AbsoluteFill style={{ 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    zIndex: 10,
                    padding: '0 60px', // Increased padding
                }}>
                    {/* Find the index of the active caption */}
                    {(() => {
                        const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);
                        
                        if (!activeCaption) return null;

                        return (
                            <div style={{
                                fontFamily: 'Montserrat, sans-serif',
                                fontSize: 52, // Slightly larger
                                fontWeight: 800,
                                color: 'white',
                                textShadow: '0 0 15px rgba(0,0,0,0.8), 0 0 30px rgba(255,215,0,0.4)',
                                textAlign: 'center',
                                lineHeight: 1.3,
                                width: '100%',
                                maxWidth: '100%',
                            }}>
                                {activeCaption.text}
                            </div>
                        );
                    })()}
                </AbsoluteFill>
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

            {/* INFO OVERLAY (Lucky Numbers, Color, Vibe, Date) - Top Left */}
            <div style={{
                position: 'absolute',
                top: 40,
                left: 40,
                zIndex: 20,
                display: 'flex',
                flexDirection: 'column',
                gap: 10,
                fontFamily: 'Montserrat, sans-serif',
                textAlign: 'left',
            }}>
                {/* PREDICTION TYPE HEADER */}
                <div style={{
                    background: 'rgba(255,215,0,0.9)',
                    color: 'black',
                    padding: '5px 15px',
                    borderRadius: 5,
                    fontSize: 24,
                    fontWeight: 900,
                    textTransform: 'uppercase',
                    boxShadow: '0 0 15px rgba(255,215,0,0.4)',
                    alignSelf: 'flex-start',
                }}>
                    {predictionType} PREDICTION
                </div>

                {/* DATE */}
                <div style={{
                    fontSize: 20,
                    color: 'white',
                    fontWeight: 600,
                    opacity: 0.9,
                    marginTop: 2,
                    textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                }}>
                    📅 {date}
                </div>

                <div style={{ 
                    background: 'rgba(0, 0, 0, 0.6)', 
                    padding: '15px', 
                    borderRadius: 15,
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                    marginTop: 10,
                }}>
                     {/* LUCKY COLOR */}
                     {luckyColor && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <div style={{ width: 15, height: 15, borderRadius: '50%', background: luckyColor, boxShadow: '0 0 8px '+luckyColor }}></div>
                            <span style={{ fontSize: 18, color: 'white', fontWeight: 500 }}>
                                Color: <span style={{ color: luckyColor, fontWeight: 700 }}>{luckyColor}</span>
                            </span>
                        </div>
                    )}

                    {/* LUCKY NUMBERS */}
                    {luckyNumbers && luckyNumbers.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <span style={{ fontSize: 24 }}>🎰</span>
                            <span style={{ fontSize: 18, color: 'white', fontWeight: 500 }}>
                                Lucky: <span style={{ color: '#FFD700', fontWeight: 700 }}>{luckyNumbers.join(', ')}</span>
                            </span>
                        </div>
                    )}

                    {/* MONTHLY VIBE */}
                    {monthlyVibe && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <span style={{ fontSize: 24 }}>✨</span>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <span style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>current vibe</span>
                                <span style={{ fontSize: 18, color: 'white', fontWeight: 700 }}>
                                    {monthlyVibe}
                                </span>
                            </div>
                        </div>
                    )}
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

            {/* SCREEN FLASH (Surprise Moments) */}
            {flashOpacity > 0 && (
                <AbsoluteFill style={{
                    zIndex: 25,
                    background: 'radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,215,0,0.8) 50%, transparent 100%)',
                    opacity: flashOpacity,
                    pointerEvents: 'none',
                    mixBlendMode: 'overlay',
                }} />
            )}
            
            {/* DARK PULSE (Warning Moments) */}
            {darkPulseOpacity > 0 && (
                <AbsoluteFill style={{
                    zIndex: 25,
                    background: 'radial-gradient(ellipse at center, transparent 30%, rgba(139,0,0,0.6) 70%, rgba(0,0,0,0.8) 100%)',
                    opacity: darkPulseOpacity,
                    pointerEvents: 'none',
                }} />
            )}
            
            {/* WARNING BORDER PULSE */}
            {hasWarning && (
                <AbsoluteFill style={{
                    zIndex: 24,
                    border: `${4 + Math.sin(frame * 0.2) * 2}px solid rgba(255,0,0,${0.3 + Math.sin(frame * 0.15) * 0.2})`,
                    borderRadius: 0,
                    pointerEvents: 'none',
                    boxShadow: `inset 0 0 ${50 + Math.sin(frame * 0.1) * 20}px rgba(139,0,0,0.4)`,
                }} />
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
            {enableNoise && (
            <AbsoluteFill style={{ 
                zIndex: 12,
                pointerEvents: 'none',
                opacity: 0.05,
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
            }} />
            )}
            
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

const BackgroundClip: React.FC<{src: AssetSpec, index: number, total: number}> = ({ src, index, total }) => {
    const frame = useCurrentFrame();
    
    // Smooth Scale Ken Burns
    const scale = interpolate(frame, [0, 150], [1.0, 1.15], { extrapolateRight: 'clamp' });
    
    const style = {
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        transform: `scale(${scale})`
    };

    // Handle Image Sequence (Robust CI method)
    if (typeof src === 'object' && src.type === 'sequence') {
        const { prefix, count } = src;
        // Loop the sequence
        const sequenceFrame = frame % count;
        // Construct path: prefix + frame_XXXX.jpg
        const imagePath = `${prefix}frame_${String(sequenceFrame).padStart(4, '0')}.jpg`;
        return <Img src={staticFile(imagePath)} style={style} placeholder={undefined} onResize={undefined} onResizeCapture={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} />;
    }

    // Handle Legacy Video/Image (String path)
    const srcString = src as string;
    // Fallback to a known good image if empty
    const finalSrc = srcString || "https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg";
    
    // Check if source is strictly a video file to avoid errors
    const isVideo = finalSrc.toLowerCase().endsWith('.mp4');

    if (isVideo) {
        // Use staticFile for local assets to prevent timeouts
        // Reverted to Video component as OffthreadVideo was too slow on CI (12s/frame)
        // Global timeout increased to 300000ms to handle slow seeking
        return <Video src={staticFile(finalSrc)} style={style} muted loop />;
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
                
                // Check for underline keywords
                const hasUnderline = UNDERLINE_KEYWORDS.some(kw => 
                    word.toLowerCase().replace(/[^a-z]/g, '').includes(kw)
                );
                
                // Animate individual word with slight delay
                const wordDelay = i * 2;
                const wordScale = interpolate(timeInCaption, [wordDelay, wordDelay + 5], [0.8, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
                const wordOpacity = interpolate(timeInCaption, [wordDelay, wordDelay + 3], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
                
                // Gold flash for highlight words
                const goldPulse = isHighlight ? Math.sin((timeInCaption + i) * 0.2) * 0.3 + 0.7 : 0;
                
                // Animated underline width (expands from 0 to 100%)
                const underlineWidth = hasUnderline ? 
                    interpolate(timeInCaption, [wordDelay, wordDelay + 10], [0, 100], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' }) : 0;
                
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
                    </span>
                );
            })}
        </div>
    );
};
