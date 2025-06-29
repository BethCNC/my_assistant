import Head from 'next/head';
import Conditions from '../components/diagnoses/Conditions';

export default function ConditionsPage() {
  return (
    <>
      <Head>
        <title>Health Conditions | Beth's Health Journey</title>
        <meta name="description" content="Manage and track your health conditions" />
      </Head>
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">My Health Conditions</h1>
          <Conditions />
        </div>
      </div>
    </>
  );
} 