'use client';

import { motion } from 'framer-motion';
import TextType from '@/components/ui/TextType';
import { TextRevealByWord } from '@/components/ui/TextRevealByWord';
import { BarChart2, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function ComponentsDemo() {
  return (
    <div className="bg-[#050810] min-h-screen text-white">
      {/* Navigation */}
      <nav className="relative z-10 flex items-center px-8 py-5 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <BarChart2 size={17} className="text-white" />
          </div>
          <span className="text-white font-semibold text-sm tracking-tight">Asklytics</span>
        </div>
        <div className="ml-auto">
          <Link href="/" className="text-slate-300 hover:text-white transition-colors">
            Back to Home
          </Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-6 py-20">
        {/* TextType Component Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-8 text-white">
            Component Showcase
          </h1>

          {/* TextType Demo 1: Basic */}
          <div className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold mb-4 text-indigo-300">
              TextType: Basic Typing Animation
            </h2>
            <div className="bg-[#050810] rounded-lg p-6 mb-4">
              <TextType
                text="Welcome to the Asklytics. Type any question and get instant visualizations!"
                typingSpeed={50}
                showCursor={true}
                cursorCharacter="|"
                className="text-lg text-slate-200"
              />
            </div>
            <p className="text-slate-400 text-sm">
              <strong>Props:</strong> typingSpeed=50, showCursor=true, no loop
            </p>
          </div>

          {/* TextType Demo 2: Multiple Texts */}
          <div className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold mb-4 text-indigo-300">
              TextType: Multiple Texts with Loop
            </h2>
            <div className="bg-[#050810] rounded-lg p-6 mb-4">
              <TextType
                text={[
                  "What is the total revenue by category?",
                  "Show me monthly sales trends",
                  "Compare average ratings by region",
                  "Which products have the highest demand?"
                ]}
                typingSpeed={45}
                deletingSpeed={30}
                pauseDuration={1500}
                loop={true}
                showCursor={true}
                cursorCharacter="▌"
                className="text-lg text-indigo-300 min-h-[2rem]"
              />
            </div>
            <p className="text-slate-400 text-sm">
              <strong>Props:</strong> Multiple texts, loop=true, pauseDuration=1500, cursorCharacter="▌"
            </p>
          </div>

          {/* TextType Demo 3: Variable Speed */}
          <div className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold mb-4 text-indigo-300">
              TextType: Variable Speed (Natural Typing)
            </h2>
            <div className="bg-[#050810] rounded-lg p-6 mb-4">
              <TextType
                text="Notice how this text types at different speeds, just like a real person typing!"
                typingSpeed={50}
                variableSpeed={{ min: 20, max: 80 }}
                showCursor={true}
                cursorCharacter="_"
                className="text-lg text-cyan-300"
              />
            </div>
            <p className="text-slate-400 text-sm">
              <strong>Props:</strong> variableSpeed with <code>min: 20, max: 80</code> for natural feel
            </p>
          </div>

          {/* TextType Demo 4: Colored Text */}
          <div className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold mb-4 text-indigo-300">
              TextType: Multiple Colors
            </h2>
            <div className="bg-[#050810] rounded-lg p-6 mb-4">
              <TextType
                text={[
                  "Analytics",
                  "Dashboard",
                  "Intelligence"
                ]}
                textColors={["#ff5c7a", "#8a5cff", "#00ffd1"]}
                typingSpeed={60}
                deletingSpeed={40}
                pauseDuration={1500}
                loop={true}
                showCursor={true}
                cursorCharacter="→"
                className="text-3xl font-bold min-h-[3rem] flex items-center"
              />
            </div>
            <p className="text-slate-400 text-sm">
              <strong>Props:</strong> textColors array for each text, colored cursor
            </p>
          </div>
        </motion.section>

        {/* TextRevealByWord Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-20"
        >
          <div className="bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8">
            <h2 className="text-2xl font-bold mb-4 text-indigo-300">
              TextRevealByWord: Scroll-Triggered Reveal
            </h2>
            <p className="text-slate-400 mb-6">
              Scroll down to see how each word reveals as you scroll (word-by-word animation).
            </p>
            <TextRevealByWord
              text="This text reveals word by word as you scroll down the page. Each word fades in with a smooth opacity transition, creating an engaging reading experience."
              className="py-20"
            />
          </div>
        </motion.section>

        {/* Usage Guide */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-20"
        >
          <h2 className="text-2xl font-bold mb-8 text-indigo-300">Usage Guide</h2>

          <div className="space-y-6">
            {/* TextType Usage */}
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">TextType Component</h3>
              <pre className="bg-[#050810] p-4 rounded text-sm overflow-x-auto text-slate-300">
{`import TextType from '@/components/ui/TextType';

<TextType
  text="Single text or array of strings"
  typingSpeed={50}           // ms per character
  deletingSpeed={30}         // ms per character deletion
  pauseDuration={2000}       // ms pause between texts
  loop={true}                // repeat the animation
  showCursor={true}          // show typing cursor
  cursorCharacter="|"        // cursor symbol
  variableSpeed={{ min: 20, max: 80 }}  // random speed (min-max range)
  textColors={['#color1', '#color2']}   // per-text colors
  className="text-lg"        // Tailwind or CSS classes for styling
/>`}
              </pre>
            </div>

            {/* TextRevealByWord Usage */}
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">TextRevealByWord Component</h3>
              <pre className="bg-[#050810] p-4 rounded text-sm overflow-x-auto text-slate-300">
{`import { TextRevealByWord } from '@/components/ui/TextRevealByWord';

<TextRevealByWord
  text="Your text here with multiple words"
  className="py-20"  // optional styling
/>`}
              </pre>
            </div>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold mb-6 text-white">
            Ready to explore your data?
          </h2>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
            >
              Try Demo
              <ArrowRight size={16} />
            </Link>
            <Link
              href="/"
              className="flex items-center gap-2 text-slate-200 hover:text-white border border-white/20 hover:border-white/40 px-8 py-3.5 rounded-xl transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
