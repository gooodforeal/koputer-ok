import React from 'react';

interface BackgroundDecorationsProps {
  variant?: 'hero' | 'features' | 'steps' | 'pricing' | 'faq' | 'testimonials' | 'cta';
}

const BackgroundDecorations: React.FC<BackgroundDecorationsProps> = ({ variant = 'hero' }) => {
  const renderHeroDecorations = () => (
    <>
      {/* SVG декоративные элементы */}
      <svg
        className="absolute top-20 left-10 w-32 h-32 text-blue-300 dark:text-blue-700 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <polygon points="50,10 90,30 90,70 50,90 10,70 10,30" />
      </svg>
      
      <svg
        className="absolute bottom-20 right-10 w-24 h-24 text-purple-300 dark:text-purple-700 opacity-25"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
      
      <svg
        className="absolute top-1/2 right-1/4 w-16 h-16 text-cyan-300 dark:text-cyan-700 opacity-30"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <rect x="20" y="20" width="60" height="60" rx="10" />
      </svg>
    </>
  );

  const renderFeaturesDecorations = () => (
    <>
      <svg
        className="absolute top-10 left-20 w-20 h-20 text-blue-200 dark:text-blue-800 opacity-15"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <path d="M50 10 L90 30 L90 70 L50 90 L10 70 L10 30 Z" />
      </svg>
      
      <svg
        className="absolute bottom-10 right-20 w-16 h-16 text-purple-200 dark:text-purple-800 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
    </>
  );

  const renderStepsDecorations = () => (
    <>
      <svg
        className="absolute top-20 left-10 w-24 h-24 text-blue-200 dark:text-blue-800 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <polygon points="50,10 90,30 90,70 50,90 10,70 10,30" />
      </svg>
      
      <svg
        className="absolute bottom-20 right-10 w-32 h-32 text-purple-200 dark:text-purple-800 opacity-15"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
    </>
  );

  const renderPricingDecorations = () => (
    <>
      <svg
        className="absolute top-20 left-20 w-40 h-40 text-white opacity-5"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <polygon points="50,10 90,30 90,70 50,90 10,70 10,30" />
      </svg>
      
      <svg
        className="absolute bottom-20 right-20 w-60 h-60 text-white opacity-3"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
    </>
  );

  const renderFaqDecorations = () => (
    <>
      <svg
        className="absolute top-20 right-20 w-16 h-16 text-blue-300 dark:text-blue-700 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <rect x="20" y="20" width="60" height="60" rx="10" />
      </svg>
      
      <svg
        className="absolute bottom-20 left-20 w-20 h-20 text-purple-300 dark:text-purple-700 opacity-15"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
    </>
  );

  const renderTestimonialsDecorations = () => (
    <>
      <svg
        className="absolute top-10 left-1/4 w-24 h-24 text-blue-400 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <polygon points="50,10 90,30 90,70 50,90 10,70 10,30" />
      </svg>
      
      <svg
        className="absolute bottom-10 right-1/4 w-32 h-32 text-purple-400 opacity-15"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
    </>
  );

  const renderCtaDecorations = () => (
    <>
      <svg
        className="absolute top-20 right-20 w-28 h-28 text-blue-200 dark:text-blue-800 opacity-20"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <rect x="20" y="20" width="60" height="60" rx="10" />
      </svg>
      
      <svg
        className="absolute bottom-20 left-20 w-24 h-24 text-purple-200 dark:text-purple-800 opacity-15"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <circle cx="50" cy="50" r="40" />
      </svg>
      
      <svg
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-40 h-40 text-blue-300 dark:text-blue-700 opacity-10"
        viewBox="0 0 100 100"
        fill="currentColor"
      >
        <polygon points="50,10 90,30 90,70 50,90 10,70 10,30" />
      </svg>
    </>
  );

  const renderDecorations = () => {
    switch (variant) {
      case 'hero':
        return renderHeroDecorations();
      case 'features':
        return renderFeaturesDecorations();
      case 'steps':
        return renderStepsDecorations();
      case 'pricing':
        return renderPricingDecorations();
      case 'faq':
        return renderFaqDecorations();
      case 'testimonials':
        return renderTestimonialsDecorations();
      case 'cta':
        return renderCtaDecorations();
      default:
        return renderHeroDecorations();
    }
  };

  return <>{renderDecorations()}</>;
};

export default BackgroundDecorations;
