import { useState, useEffect } from 'react';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Plane, Car, Ship } from 'lucide-react';

interface TransportCalculatorProps {
  onUpdate: (co2: number) => void;
}

// CO2 emissions in kg per passenger per km
const EMISSION_FACTORS = {
  plane_international: 0.255,
  plane_domestic: 0.133,
  car: 0.192,
  bus: 0.089,
  ferry: 0.115,
  helicopter: 0.250,
};

export function TransportCalculator({ onUpdate }: TransportCalculatorProps) {
  const [transportType, setTransportType] = useState('plane_international');
  const [distance, setDistance] = useState('');
  const [passengers, setPassengers] = useState('1');

  useEffect(() => {
    const dist = parseFloat(distance) || 0;
    const pass = parseInt(passengers) || 1;
    const factor = EMISSION_FACTORS[transportType as keyof typeof EMISSION_FACTORS];
    const total = dist * factor * pass;
    onUpdate(total);
  }, [transportType, distance, passengers, onUpdate]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-blue-600 mb-4">
        <Plane className="size-5" />
        <h3 className="font-semibold">Transportation Emissions</h3>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="transport-type">Transport Type</Label>
          <Select value={transportType} onValueChange={setTransportType}>
            <SelectTrigger id="transport-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="plane_international">✈️ International Flight</SelectItem>
              <SelectItem value="plane_domestic">✈️ Domestic Flight</SelectItem>
              <SelectItem value="helicopter">🚁 Helicopter</SelectItem>
              <SelectItem value="car">🚗 Car/SUV</SelectItem>
              <SelectItem value="bus">🚌 Bus</SelectItem>
              <SelectItem value="ferry">⛴️ Ferry</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-gray-500 mt-1">
            Select the primary mode of transport to Kamchatka
          </p>
        </div>

        <div>
          <Label htmlFor="distance">Distance (km)</Label>
          <Input
            id="distance"
            type="number"
            placeholder="e.g., 6800"
            value={distance}
            onChange={(e) => setDistance(e.target.value)}
            min="0"
          />
          <p className="text-xs text-gray-500 mt-1">
            Round-trip distance. Example: Moscow to Kamchatka ≈ 6,800 km
          </p>
        </div>

        <div>
          <Label htmlFor="passengers">Number of Passengers</Label>
          <Input
            id="passengers"
            type="number"
            placeholder="1"
            value={passengers}
            onChange={(e) => setPassengers(e.target.value)}
            min="1"
          />
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-semibold text-sm mb-2">Common Routes to Kamchatka:</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Moscow → Petropavlovsk-Kamchatsky: ~6,800 km</li>
          <li>• Tokyo → Petropavlovsk-Kamchatsky: ~2,400 km</li>
          <li>• Seoul → Petropavlovsk-Kamchatsky: ~2,000 km</li>
          <li>• Vladivostok → Petropavlovsk-Kamchatsky: ~2,400 km</li>
        </ul>
      </div>
    </div>
  );
}
