import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Plane, Car, Hotel, UtensilsCrossed, Activity, Calculator } from 'lucide-react';
import type { TripData } from '../types';

interface TravelFormProps {
  onCalculate: (data: TripData) => void;
}

export function TravelForm({ onCalculate }: TravelFormProps) {
  const [formData, setFormData] = useState<TripData>({
    flightDistance: 0,
    flightClass: 'economy',
    groundTransport: 'car',
    groundDistance: 0,
    accommodation: 'hotel',
    nights: 1,
    activities: [],
    diet: 'mixed',
  });

  const activities = [
    { id: 'helicopter', label: 'Helicopter Tour', emission: '~150 kg' },
    { id: 'snowmobile', label: 'Snowmobile Excursion', emission: '~80 kg' },
    { id: 'atv', label: 'ATV Tour', emission: '~60 kg' },
    { id: 'boat', label: 'Boat Tour', emission: '~40 kg' },
    { id: 'skiing', label: 'Skiing/Snowboarding', emission: '~5 kg' },
    { id: 'hiking', label: 'Hiking', emission: '0 kg' },
  ];

  const handleActivityToggle = (activityId: string) => {
    setFormData((prev) => ({
      ...prev,
      activities: prev.activities.includes(activityId)
        ? prev.activities.filter((a) => a !== activityId)
        : [...prev.activities, activityId],
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCalculate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Transportation */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Plane className="w-5 h-5 text-blue-600" />
            <CardTitle>Transportation to Kamchatka</CardTitle>
          </div>
          <CardDescription>How will you travel to and within Kamchatka?</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="flightDistance">Flight Distance (km)</Label>
              <Input
                id="flightDistance"
                type="number"
                min="0"
                value={formData.flightDistance || ''}
                onChange={(e) =>
                  setFormData({ ...formData, flightDistance: Number(e.target.value) })
                }
                placeholder="e.g., 6500 from Moscow"
              />
              <p className="text-slate-500">Tip: Moscow to Kamchatka ~6,500 km</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="flightClass">Flight Class</Label>
              <Select
                value={formData.flightClass}
                onValueChange={(value: 'economy' | 'business') =>
                  setFormData({ ...formData, flightClass: value })
                }
              >
                <SelectTrigger id="flightClass">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="economy">Economy</SelectItem>
                  <SelectItem value="business">Business</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="border-t pt-4 mt-4">
            <div className="flex items-center gap-2 mb-4">
              <Car className="w-5 h-5 text-blue-600" />
              <h4 className="font-medium">Ground Transportation in Kamchatka</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="groundTransport">Transport Type</Label>
                <Select
                  value={formData.groundTransport}
                  onValueChange={(value: 'car' | 'bus' | 'train' | 'none') =>
                    setFormData({ ...formData, groundTransport: value })
                  }
                >
                  <SelectTrigger id="groundTransport">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="car">Rental Car / Taxi</SelectItem>
                    <SelectItem value="bus">Bus / Shuttle</SelectItem>
                    <SelectItem value="train">Train</SelectItem>
                    <SelectItem value="none">None</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="groundDistance">Distance (km)</Label>
                <Input
                  id="groundDistance"
                  type="number"
                  min="0"
                  value={formData.groundDistance || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, groundDistance: Number(e.target.value) })
                  }
                  placeholder="e.g., 500"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Accommodation */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Hotel className="w-5 h-5 text-blue-600" />
            <CardTitle>Accommodation</CardTitle>
          </div>
          <CardDescription>Where will you stay during your visit?</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="accommodation">Accommodation Type</Label>
              <Select
                value={formData.accommodation}
                onValueChange={(value: 'hotel' | 'hostel' | 'ecolodge' | 'camping') =>
                  setFormData({ ...formData, accommodation: value })
                }
              >
                <SelectTrigger id="accommodation">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hotel">Hotel (30 kg CO₂/night)</SelectItem>
                  <SelectItem value="hostel">Hostel/Guesthouse (15 kg CO₂/night)</SelectItem>
                  <SelectItem value="ecolodge">Eco-Lodge (10 kg CO₂/night)</SelectItem>
                  <SelectItem value="camping">Camping (2 kg CO₂/night)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="nights">Number of Nights</Label>
              <Input
                id="nights"
                type="number"
                min="1"
                value={formData.nights}
                onChange={(e) => setFormData({ ...formData, nights: Number(e.target.value) })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Activities */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <CardTitle>Activities & Excursions</CardTitle>
          </div>
          <CardDescription>Select the activities you plan to participate in</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg border">
                <Checkbox
                  id={activity.id}
                  checked={formData.activities.includes(activity.id)}
                  onCheckedChange={() => handleActivityToggle(activity.id)}
                />
                <div className="grid gap-1.5 leading-none">
                  <label
                    htmlFor={activity.id}
                    className="font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {activity.label}
                  </label>
                  <p className="text-slate-500">{activity.emission}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Food */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <UtensilsCrossed className="w-5 h-5 text-blue-600" />
            <CardTitle>Food & Diet</CardTitle>
          </div>
          <CardDescription>What type of diet will you follow during your trip?</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="diet">Diet Type</Label>
            <Select
              value={formData.diet}
              onValueChange={(value: 'meat' | 'mixed' | 'vegetarian' | 'vegan') =>
                setFormData({ ...formData, diet: value })
              }
            >
              <SelectTrigger id="diet">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="meat">Meat-heavy (7.2 kg CO₂/day)</SelectItem>
                <SelectItem value="mixed">Mixed Diet (5.6 kg CO₂/day)</SelectItem>
                <SelectItem value="vegetarian">Vegetarian (3.8 kg CO₂/day)</SelectItem>
                <SelectItem value="vegan">Vegan (2.9 kg CO₂/day)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Button type="submit" size="lg" className="w-full md:w-auto">
        <Calculator className="w-5 h-5 mr-2" />
        Calculate My Carbon Footprint
      </Button>
    </form>
  );
}
