import { useState, useEffect } from 'react';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Home } from 'lucide-react';

interface AccommodationCalculatorProps {
  onUpdate: (co2: number) => void;
}

// CO2 emissions in kg per night per person
const ACCOMMODATION_EMISSIONS = {
  hotel_luxury: 30,
  hotel_standard: 20,
  guesthouse: 12,
  hostel: 8,
  camping: 2,
  eco_lodge: 5,
};

export function AccommodationCalculator({ onUpdate }: AccommodationCalculatorProps) {
  const [accommodationType, setAccommodationType] = useState('hotel_standard');
  const [nights, setNights] = useState('');
  const [guests, setGuests] = useState('1');

  useEffect(() => {
    const nightCount = parseFloat(nights) || 0;
    const guestCount = parseInt(guests) || 1;
    const emissionPerNight = ACCOMMODATION_EMISSIONS[accommodationType as keyof typeof ACCOMMODATION_EMISSIONS];
    const total = nightCount * emissionPerNight * guestCount;
    onUpdate(total);
  }, [accommodationType, nights, guests, onUpdate]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-green-600 mb-4">
        <Home className="size-5" />
        <h3 className="font-semibold">Accommodation Emissions</h3>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="accommodation-type">Accommodation Type</Label>
          <Select value={accommodationType} onValueChange={setAccommodationType}>
            <SelectTrigger id="accommodation-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hotel_luxury">🏨 Luxury Hotel</SelectItem>
              <SelectItem value="hotel_standard">🏨 Standard Hotel</SelectItem>
              <SelectItem value="guesthouse">🏠 Guesthouse</SelectItem>
              <SelectItem value="hostel">🛏️ Hostel</SelectItem>
              <SelectItem value="eco_lodge">🌿 Eco-Lodge</SelectItem>
              <SelectItem value="camping">⛺ Camping/Tent</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="nights">Number of Nights</Label>
          <Input
            id="nights"
            type="number"
            placeholder="e.g., 7"
            value={nights}
            onChange={(e) => setNights(e.target.value)}
            min="0"
          />
          <p className="text-xs text-gray-500 mt-1">
            Total nights staying in Kamchatka
          </p>
        </div>

        <div>
          <Label htmlFor="guests">Number of Guests</Label>
          <Input
            id="guests"
            type="number"
            placeholder="1"
            value={guests}
            onChange={(e) => setGuests(e.target.value)}
            min="1"
          />
        </div>
      </div>

      <div className="bg-green-50 p-4 rounded-lg">
        <h4 className="font-semibold text-sm mb-2">💡 Eco-Friendly Tips:</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Choose eco-lodges with sustainable practices</li>
          <li>• Camping has the lowest carbon footprint</li>
          <li>• Look for accommodations with renewable energy</li>
          <li>• Reuse towels and minimize water usage</li>
        </ul>
      </div>
    </div>
  );
}
