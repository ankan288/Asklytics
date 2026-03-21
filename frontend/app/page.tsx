'use client'

import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'

const ColorBends = dynamic(() => import('@/components/ui/ColorBends'), { ssr: false })

export default function LandingPage() {
  const router = useRouter()

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-black">
      {/* ColorBends Background */}
      <div className="absolute inset-0 w-full h-full">
        <ColorBends
          colors={['#ff5c7a', '#8a5cff', '#00ffd1']}
          rotation={0}
          speed={0.2}
          scale={1}
          frequency={1}
          warpStrength={1}
          mouseInfluence={1}
          parallax={0.5}
          noise={0.1}
          transparent
          autoRotate={0}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full min-h-screen flex flex-col">
        {/* Navigation */}
        <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="text-white font-bold text-xl"
          >
            Asklytics
          </motion.div>
        </nav>

        {/* Hero Section */}
        <div className="flex-1 flex items-center justify-center px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center max-w-3xl"
          >
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-8 leading-tight">
              You have the power to reshape your own destiny
            </h1>

            <p className="text-lg md:text-xl text-white/70 mb-12 leading-relaxed">
              No SQL. No code. Just ask.
            </p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex gap-4 justify-center flex-wrap"
            >
              <button
                onClick={() => router.push('/register')}
                className="px-8 py-3 bg-white text-black font-semibold rounded-lg hover:bg-white/90 transition shadow-lg hover:shadow-xl"
              >
                Get Started
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-8 py-3 border border-white/30 text-white font-semibold rounded-lg hover:bg-white/10 backdrop-blur transition"
              >
                Demo
              </button>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
