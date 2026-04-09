import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Footer } from "@/components/landing/Footer";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-brand-bg text-white overflow-x-hidden">
      <Hero />
      <Features />
      <HowItWorks />
      <Footer />
    </main>
  );
}
