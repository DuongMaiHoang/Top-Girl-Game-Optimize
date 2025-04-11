
import React, { useEffect, useState } from 'react';

const Card = ({ children }) => <div className="bg-white rounded-xl shadow p-4">{children}</div>;
const CardContent = ({ children }) => <div>{children}</div>;
const Button = ({ children, ...props }) => <button className="px-4 py-2 bg-blue-500 text-white rounded" {...props}>{children}</button>;
const Input = (props) => <input className="border rounded px-2 py-1 w-full" {...props} />;
const Label = ({ children }) => <label className="block mb-1 font-medium">{children}</label>;

export default function Dashboard() {
  const [buildings, setBuildings] = useState([]);
  const [result, setResult] = useState(null);

  const [moneyDisplay, setMoneyDisplay] = useState("10000");
  const [goldDisplay, setGoldDisplay] = useState("2");
  const [tradeXDisplay, setTradeXDisplay] = useState("2");
  const [tradeYDisplay, setTradeYDisplay] = useState("1");

  const [money, setMoney] = useState(10000);
  const [gold, setGold] = useState(2);
  const [tradeX, setTradeX] = useState(2);
  const [tradeY, setTradeY] = useState(1);

  const displayToValue = (input) => {
    if (typeof input !== 'string') return Number(input) || 0;
    const num = parseFloat(input);
    if (isNaN(num)) return 0;
    const lower = input.toLowerCase();
    if (lower.includes('k')) return num * 1_000;
    if (lower.includes('m')) return num * 1_000_000;
    if (lower.includes('b')) return num * 1_000_000_000;
    if (lower.includes('t')) return num * 1_000_000_000_000;
    return num;
  };

  const fetchBuildings = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/buildings`);
      if (!res.ok) throw new Error("Failed to fetch buildings");
      const data = await res.json();
      setBuildings(data);
    } catch (err) {
      console.error("Error loading buildings:", err);
    }
  };

  const fetchOptimizeHistory = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/optimize/last`);
      if (res.ok) {
        const data = await res.json();
        setMoneyDisplay(data.current_money.toString());
        setGoldDisplay(data.current_gold.toString());
        setTradeXDisplay(data.trade_x.toString());
        setTradeYDisplay(data.trade_y.toString());
        setMoney(data.current_money);
        setGold(data.current_gold);
        setTradeX(data.trade_x);
        setTradeY(data.trade_y);
      }
    } catch (e) {
      console.warn('No previous optimize inputs available');
    }
  };

  const optimize = async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_money: money,
        current_gold: gold,
        trade_x: tradeX,
        trade_y: tradeY,
        session_seconds: 10800
      })
    });
    const data = await res.json();
    setResult(data);
  };

  useEffect(() => {
    fetchBuildings();
    fetchOptimizeHistory();
  }, []);

  return (
    <div className="p-4 grid gap-4">
      <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <Label>Money</Label>
          <Input type="text" value={moneyDisplay} onChange={e => {
            setMoneyDisplay(e.target.value);
            setMoney(displayToValue(e.target.value));
          }} />
        </div>
        <div>
          <Label>Gold</Label>
          <Input type="text" value={goldDisplay} onChange={e => {
            setGoldDisplay(e.target.value);
            setGold(displayToValue(e.target.value));
          }} />
        </div>
        <div>
          <Label>Trade X</Label>
          <Input type="text" value={tradeXDisplay} onChange={e => {
            setTradeXDisplay(e.target.value);
            setTradeX(displayToValue(e.target.value));
          }} />
        </div>
        <div>
          <Label>Trade Y</Label>
          <Input type="text" value={tradeYDisplay} onChange={e => {
            setTradeYDisplay(e.target.value);
            setTradeY(displayToValue(e.target.value));
          }} />
        </div>
      </div>

      <Button className="w-fit mt-2" onClick={optimize}>Optimize</Button>

      {result !== null && (
        <div>
          <h2 className="text-xl font-semibold mt-4">Best Upgrade Plan</h2>
          <p>Total Income Earned: ${result.total_income_earned}</p>
          <p>Final Income/sec: ${result.final_income_per_second}</p>
          <div className="grid gap-2 mt-4">
            {Array.isArray(result.upgrade_plan) && result.upgrade_plan.length > 0 ? (
              result.upgrade_plan.map((step, i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <p className="font-semibold">{step.building_name}</p>
                    <p>Upgrade at: {step.upgrade_time}s</p>
                    <p>New Total Income: {step.new_total_income}</p>
                    <p>New Level: {step.curr_level}</p>
                  </CardContent>
                </Card>
              ))
            ) : (
              <p className="text-gray-500 italic">No upgrades planned.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
