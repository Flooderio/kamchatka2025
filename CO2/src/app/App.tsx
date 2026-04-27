import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { TransportCalculator } from './components/TransportCalculator';
import { AccommodationCalculator } from './components/AccommodationCalculator';
import { ActivitiesCalculator } from './components/ActivitiesCalculator';
import { ResultsSummary } from './components/ResultsSummary';
import { Mountain, Leaf } from 'lucide-react';

export interface CO2Data {
  transport: number;
  accommodation: number;
  activities: number;
}

export default function App() {
  const [co2Data, setCO2Data] = useState<CO2Data>({
    transport: 0,
    accommodation: 0,
    activities: 0,
  });

  const updateTransport = (value: number) => {
    setCO2Data(prev => ({ ...prev, transport: value }));
  };

  const updateAccommodation = (value: number) => {
    setCO2Data(prev => ({ ...prev, accommodation: value }));
  };

  const updateActivities = (value: number) => {
    setCO2Data(prev => ({ ...prev, activities: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Mountain className="size-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Kamchatka CO₂ Calculator</h1>
            <Leaf className="size-12 text-green-600" />
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Calculate the carbon footprint of your mountain tourism adventure in Kamchatka
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Calculator Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Calculate Your Carbon Footprint</CardTitle>
                <CardDescription>
                  Enter details about your trip to estimate CO₂ emissions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="transport" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="transport">Transport</TabsTrigger>
                    <TabsTrigger value="accommodation">Accommodation</TabsTrigger>
                    <TabsTrigger value="activities">Activities</TabsTrigger>
                  </TabsList>

                  <TabsContent value="transport" className="mt-6">
                    <TransportCalculator onUpdate={updateTransport} />
                  </TabsContent>

                  <TabsContent value="accommodation" className="mt-6">
                    <AccommodationCalculator onUpdate={updateAccommodation} />
                  </TabsContent>

                  <TabsContent value="activities" className="mt-6">
                    <ActivitiesCalculator onUpdate={updateActivities} />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-1">
            <ResultsSummary data={co2Data} />
          </div>
        </div>

        {/* Info Footer */}
        <Card className="mt-6 bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-700">
              <strong>About Kamchatka:</strong> The Kamchatka Peninsula is a pristine wilderness
              in Russia's Far East, featuring over 160 volcanoes, diverse wildlife, and unique
              geothermal landscapes. Sustainable tourism helps preserve this UNESCO World Heritage site
              for future generations.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
