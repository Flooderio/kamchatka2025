import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { CO2Data } from '../App';
import { TrendingUp, Leaf, AlertCircle } from 'lucide-react';

interface ResultsSummaryProps {
  data: CO2Data;
}

export function ResultsSummary({ data }: ResultsSummaryProps) {
  const total = data.transport + data.accommodation + data.activities;
  const maxValue = Math.max(total, 1);

  // Calculate percentages
  const transportPercent = total > 0 ? (data.transport / total) * 100 : 0;
  const accommodationPercent = total > 0 ? (data.accommodation / total) * 100 : 0;
  const activitiesPercent = total > 0 ? (data.activities / total) * 100 : 0;

  // Determine impact level
  const getImpactLevel = (total: number) => {
    if (total === 0) return { label: 'Not calculated', color: 'text-gray-500', bgColor: 'bg-gray-100' };
    if (total < 500) return { label: 'Low Impact', color: 'text-green-600', bgColor: 'bg-green-100' };
    if (total < 1500) return { label: 'Moderate Impact', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    if (total < 3000) return { label: 'High Impact', color: 'text-orange-600', bgColor: 'bg-orange-100' };
    return { label: 'Very High Impact', color: 'text-red-600', bgColor: 'bg-red-100' };
  };

  const impact = getImpactLevel(total);

  // Trees needed to offset (1 tree absorbs ~21 kg CO2/year)
  const treesNeeded = Math.ceil(total / 21);

  return (
    <div className="space-y-4">
      {/* Total Emissions Card */}
      <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="size-5" />
            Total CO₂ Emissions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-5xl font-bold mb-2">
            {total.toFixed(1)}
            <span className="text-2xl ml-2">kg</span>
          </div>
          <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${impact.bgColor} ${impact.color}`}>
            {impact.label}
          </div>
        </CardContent>
      </Card>

      {/* Breakdown Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Emissions Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">✈️ Transport</span>
              <span className="font-semibold">{data.transport.toFixed(1)} kg ({transportPercent.toFixed(0)}%)</span>
            </div>
            <Progress value={transportPercent} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">🏨 Accommodation</span>
              <span className="font-semibold">{data.accommodation.toFixed(1)} kg ({accommodationPercent.toFixed(0)}%)</span>
            </div>
            <Progress value={accommodationPercent} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">🎿 Activities</span>
              <span className="font-semibold">{data.activities.toFixed(1)} kg ({activitiesPercent.toFixed(0)}%)</span>
            </div>
            <Progress value={activitiesPercent} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Offset Information */}
      {total > 0 && (
        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-green-700">
              <Leaf className="size-5" />
              Carbon Offset
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-gray-700">
              To offset your carbon footprint, you would need approximately:
            </p>
            <div className="bg-white p-4 rounded-lg text-center">
              <div className="text-4xl font-bold text-green-700 mb-1">
                {treesNeeded}
              </div>
              <div className="text-sm text-gray-600">
                trees planted (absorbing CO₂ for 1 year)
              </div>
            </div>
            <div className="text-xs text-gray-600">
              <AlertCircle className="size-4 inline mr-1" />
              Consider supporting carbon offset programs or local conservation efforts in Kamchatka
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparison */}
      {total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Comparison</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="text-gray-700">
              Your trip's emissions are equivalent to:
            </p>
            <ul className="space-y-2 text-gray-600">
              <li>🚗 Driving {(total / 0.192).toFixed(0)} km by car</li>
              <li>💡 Powering a home for {(total / 30).toFixed(1)} days</li>
              <li>📱 Charging a smartphone {(total * 1000 / 8).toFixed(0)} times</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
