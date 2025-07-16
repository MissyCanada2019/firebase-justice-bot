'use client';

import { useEffect, useState } from 'react';
import { Icons } from './icons';

const FloatingLeaves = () => {
  const [leaves, setLeaves] = useState<
    { id: number; style: React.CSSProperties }[]
  >([]);

  useEffect(() => {
    const generateLeaves = () => {
      const newLeaves = Array.from({ length: 15 }).map((_, i) => {
        const duration = Math.random() * 5 + 5; // 5-10 seconds
        const delay = Math.random() * 5; // 0-5 seconds
        const left = Math.random() * 100;
        const animation = `leaf-fall ${duration}s ${delay}s infinite linear`;
        const size = Math.random() * 20 + 10; // 10-30px

        return {
          id: i,
          style: {
            position: 'fixed',
            top: '-10vh',
            left: `${left}vw`,
            width: `${size}px`,
            height: `${size}px`,
            animation,
            zIndex: -1,
            opacity: 0,
          } as React.CSSProperties,
        };
      });
      setLeaves(newLeaves);
    };

    generateLeaves();
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden z-[-1]">
      {leaves.map((leaf) => (
        <div key={leaf.id} style={leaf.style}>
          <Icons.mapleLeaf className="text-accent/20" />
        </div>
      ))}
    </div>
  );
};

export default FloatingLeaves;
