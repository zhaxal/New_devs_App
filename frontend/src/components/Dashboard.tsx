import React, { useState, useEffect } from "react";
import { RevenueSummary } from "./RevenueSummary";
import { SecureAPI } from "../lib/secureApi";


interface Property {
  id: string;           // Property unique identifier
  name: string;         // Display name
  timezone?: string;    // IANA timezone (e.g., 'Europe/Paris')
}


const Dashboard: React.FC = () => {

  const [properties, setProperties] = useState<Property[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchProperties = async () => {
      setIsLoading(true);
      try {

        const propertiesList = await SecureAPI.getDashboardProperties();
        setProperties(propertiesList);
        

        if (propertiesList && propertiesList.length > 0) {
          setSelectedProperty(propertiesList[0].id);
        }
      } catch (err) {
        setError('Failed to load properties');
        console.error('Properties fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProperties();
  }, []);


  if (isLoading) {
    return (
      <div className="p-4 lg:p-6 min-h-full">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-100 rounded w-1/3"></div>
            <div className="h-12 bg-gray-100 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-4 lg:p-6 min-h-full">
        <div className="max-w-7xl mx-auto">
          <p className="text-red-500 bg-red-50 rounded-lg p-4">{error}</p>
        </div>
      </div>
    );
  }


  return (
    <div className="p-4 lg:p-6 min-h-full">
      <div className="max-w-7xl mx-auto">

        <h1 className="text-2xl font-bold mb-6 text-gray-900">
          Property Management Dashboard
        </h1>

   
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
              <div>
                <h2 className="text-lg lg:text-xl font-medium text-gray-900 mb-2">
                  Revenue Overview
                </h2>
                <p className="text-sm lg:text-base text-gray-600">
                  Monthly performance insights for your properties
                </p>
              </div>
              

              <div className="flex flex-col sm:items-end">
                <label className="text-xs font-medium text-gray-700 mb-1">
                  Select Property
                </label>
                <select
                  value={selectedProperty}
                  onChange={(e) => setSelectedProperty(e.target.value)}
                  className="block w-full sm:w-auto min-w-[200px] px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {selectedProperty && (
              <RevenueSummary propertyId={selectedProperty} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
