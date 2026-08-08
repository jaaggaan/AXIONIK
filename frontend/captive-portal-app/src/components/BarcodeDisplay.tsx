import React from 'react';
import { QrCode, ScanLine, Sparkles, Check, Copy } from 'lucide-react';

interface BarcodeDisplayProps {
  code: string;
  discount?: string;
  className?: string;
}

export const BarcodeDisplay: React.FC<BarcodeDisplayProps> = ({ code, discount, className = "" }) => {
  const [copied, setCopied] = React.useState(false);

  // Generate deterministic bar widths from string
  const bars = React.useMemo(() => {
    const pattern = [];
    const cleanCode = (code || 'FIRSTCITIZEN15').toUpperCase();
    for (let i = 0; i < cleanCode.length; i++) {
      const charCode = cleanCode.charCodeAt(i);
      pattern.push((charCode % 3) + 1);
      pattern.push(1);
      pattern.push(((charCode * 2) % 4) + 1);
      pattern.push(1);
    }
    // Add guard bars
    return [3, 1, 1, 1, ...pattern, 1, 1, 3];
  }, [code]);

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`bg-gradient-to-b from-white via-[#faf9f5] to-[#f4efe4] border-2 border-[#d4af37]/40 rounded-2xl p-4 sm:p-5 shadow-lg relative overflow-hidden text-center space-y-3 ${className}`}>
      {/* Decorative top badge */}
      <div className="flex items-center justify-between border-b border-[#e5dec9] pb-2 text-[10px] sm:text-xs text-[#800014] font-bold uppercase tracking-wider">
        <div className="flex items-center gap-1.5">
          <ScanLine className="w-4 h-4 text-[#9e001c] animate-pulse" />
          <span>IN-STORE CASHIER BARCODE</span>
        </div>
        <span className="bg-[#9e001c]/10 text-[#9e001c] px-2 py-0.5 rounded-full font-mono text-[9px]">
          READY TO SCAN
        </span>
      </div>

      {/* Barcode Graphic Container */}
      <div className="bg-white border border-[#d6cca8] rounded-xl p-3 sm:p-4 shadow-inner relative group">
        {/* Red Laser Scanning Line effect */}
        <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-[#ff0000]/60 shadow-[0_0_8px_#ff0000] pointer-events-none group-hover:top-1/4 transition-all duration-700" />
        
        {/* Render Bars */}
        <div className="h-14 sm:h-16 w-full flex items-center justify-center gap-0.5 overflow-hidden py-1">
          {bars.map((w, idx) => (
            <div
              key={idx}
              className={`h-full ${idx % 2 === 0 ? 'bg-black' : 'bg-transparent'}`}
              style={{ width: `${Math.max(w * 1.6, 2)}px` }}
            />
          ))}
        </div>

        {/* Human Readable Code Below Bars */}
        <div className="mt-2 pt-1 border-t border-dashed border-gray-200 flex items-center justify-between px-2 font-mono">
          <span className="text-xs sm:text-sm font-extrabold tracking-[0.25em] text-[#1a1a1a]">
            *{code}*
          </span>
          <button
            onClick={copyCode}
            type="button"
            className="text-[11px] font-semibold text-[#9e001c] hover:text-[#800014] bg-[#9e001c]/5 hover:bg-[#9e001c]/10 px-2 py-0.5 rounded border border-[#9e001c]/20 transition-colors flex items-center gap-1 cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-600" />
                <span className="text-emerald-700">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Footer instruction */}
      <div className="text-[11px] text-[#555045] font-medium flex items-center justify-center gap-1.5">
        <Sparkles className="w-3.5 h-3.5 text-[#d4af37]" />
        <span>Show this barcode at any Shoppers Stop checkout billing counter</span>
      </div>
    </div>
  );
};
