import { useState, useEffect } from 'react';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { Activity } from 'lucide-react';

interface ActivitiesCalculatorProps {
  onUpdate: (co2: number) => void;
}

interface ActivityItem {
  id: string;
  name: string;
  emission: number;
  description: string;
}

const ACTIVITIES: ActivityItem[] = [
  { id: 'hiking', name: '🥾 Hiking/Trekking', emission: 5, description: 'per day' },
  { id: 'volcano', name: '🌋 Volcano Tour (vehicle)', emission: 45, description: 'per tour' },
  { id: 'helicopter', name: '🚁 Helicopter Tour', emission: 150, description: 'per hour' },
  { id: 'snowmobile', name: '🛷 Snowmobile Tour', emission: 80, description: 'per day' },
  { id: 'fishing', name: '🎣 Fishing Trip', emission: 25, description: 'per day' },
  { id: 'wildlife', name: '🐻 Wildlife Tour', emission: 35, description: 'per tour' },
  { id: 'hotsprings', name: '♨️ Hot Springs Visit', emission: 15, description: 'per visit' },
  { id: 'kayaking', name: '🛶 Sea Kayaking', emission: 8, description: 'per day' },
];

export function ActivitiesCalculator({ onUpdate }: ActivitiesCalculatorProps) {
  const [selectedActivities, setSelectedActivities] = useState<Record<string, number>>({});

  useEffect(() => {
    const total = Object.entries(selectedActivities).reduce((sum, [id, count]) => {
      const activity = ACTIVITIES.find(a => a.id === id);
      return sum + (activity ? activity.emission * count : 0);
    }, 0);
    onUpdate(total);
  }, [selectedActivities, onUpdate]);

  const handleCheckChange = (id: string, checked: boolean) => {
    setSelectedActivities(prev => {
      const updated = { ...prev };
      if (checked) {
        updated[id] = 1;
      } else {
        delete updated[id];
      }
      return updated;
    });
  };

  const handleCountChange = (id: string, value: string) => {
    const count = parseInt(value) || 0;
    if (count > 0) {
      setSelectedActivities(prev => ({ ...prev, [id]: count }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-orange-600 mb-4">
        <Activity className="size-5" />
        <h3 className="font-semibold">Activities & Tours Emissions</h3>
      </div>

      <div className="space-y-4">
        {ACTIVITIES.map(activity => (
          <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg border bg-white">
            <Checkbox
              id={activity.id}
              checked={!!selectedActivities[activity.id]}
              onCheckedChange={(checked) => handleCheckChange(activity.id, checked === true)}
              className="mt-1"
            />
            <div className="flex-1">
              <Label htmlFor={activity.id} className="cursor-pointer">
                <div className="font-medium">{activity.name}</div>
                <div className="text-xs text-gray-500">
                  ~{activity.emission} kg CO₂ {activity.description}
                </div>
              </Label>
            </div>
            {selectedActivities[activity.id] !== undefined && (
              <div className="w-20">
                <Input
                  type="number"
                  min="1"
                  value={selectedActivities[activity.id]}
                  onChange={(e) => handleCountChange(activity.id, e.target.value)}
                  className="h-8 text-sm"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="bg-orange-50 p-4 rounded-lg">
        <h4 className="font-semibold text-sm mb-2">🌍 Sustainable Tourism:</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Choose walking/hiking over motorized tours when possible</li>
          <li>• Book group tours to share emissions</li>
          <li>• Support local, eco-certified tour operators</li>
          <li>• Follow "Leave No Trace" principles</li>
        </ul>
      </div>
    </div>
  );
}
