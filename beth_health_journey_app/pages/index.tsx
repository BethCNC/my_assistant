import Head from 'next/head';
import type { NextPage } from 'next';
import Link from 'next/link';

const Home: NextPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>Health Journey</title>
        <meta name="description" content="My personal health journey tracker" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          Health Journey Dashboard
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link 
            href="/diagnoses"
            className="p-6 border rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold mb-2">Diagnoses Timeline</h2>
            <p>View your chronological diagnosis history and key medical events.</p>
          </Link>
          
          <Link 
            href="/symptoms"
            className="p-6 border rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold mb-2">Symptoms Tracker</h2>
            <p>Track and manage your symptoms and their relationship to diagnoses.</p>
          </Link>
          
          <Link 
            href="/medical-team"
            className="p-6 border rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold mb-2">Medical Team</h2>
            <p>Information about your healthcare providers and specialists.</p>
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Home; 