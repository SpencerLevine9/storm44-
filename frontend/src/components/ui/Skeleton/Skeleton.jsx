import './Skeleton.css';

/**
 * Skeleton loader component
 * Used to show placeholder content while loading
 */
function Skeleton({ 
  variant = 'text',
  width,
  height,
  borderRadius,
  count = 1,
  className = '',
  style = {},
}) {
  const baseStyle = {
    width,
    height,
    borderRadius,
    ...style,
  };

  if (count > 1) {
    return (
      <div className="skeleton-group">
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className={`skeleton skeleton--${variant} ${className}`}
            style={baseStyle}
            aria-hidden="true"
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`skeleton skeleton--${variant} ${className}`}
      style={baseStyle}
      aria-hidden="true"
    />
  );
}

/**
 * Skeleton text - multiple lines of text placeholder
 */
export function SkeletonText({ lines = 3, className = '' }) {
  return (
    <div className={`skeleton-text ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton--text"
          style={{ width: i === lines - 1 ? '60%' : '100%' }}
          aria-hidden="true"
        />
      ))}
    </div>
  );
}

/**
 * Skeleton avatar - circular placeholder
 */
export function SkeletonAvatar({ size = 40, className = '' }) {
  return (
    <div
      className={`skeleton skeleton--circular ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    />
  );
}

/**
 * Skeleton card - card placeholder with common layout
 */
export function SkeletonCard({ className = '' }) {
  return (
    <div className={`skeleton-card ${className}`} aria-hidden="true">
      <div className="skeleton skeleton--rectangular skeleton-card__image" />
      <div className="skeleton-card__content">
        <div className="skeleton skeleton--text" style={{ width: '60%' }} />
        <div className="skeleton skeleton--text" style={{ width: '100%' }} />
        <div className="skeleton skeleton--text" style={{ width: '80%' }} />
      </div>
    </div>
  );
}

/**
 * Skeleton list item - for list placeholders
 */
export function SkeletonListItem({ hasAvatar = true, className = '' }) {
  return (
    <div className={`skeleton-list-item ${className}`} aria-hidden="true">
      {hasAvatar && <div className="skeleton skeleton--circular" style={{ width: 40, height: 40 }} />}
      <div className="skeleton-list-item__content">
        <div className="skeleton skeleton--text" style={{ width: '40%', height: 14 }} />
        <div className="skeleton skeleton--text" style={{ width: '70%', height: 12 }} />
      </div>
    </div>
  );
}

export default Skeleton;
