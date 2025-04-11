import React, { useEffect, useState } from 'react';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';

export default function BuildingsCRUD() {
    const [buildings, setBuildings] = useState([]);
    const [form, setForm] = useState({
        name: '',
        curr_level: '1',
        num_employees: '1',
        curr_coefficient: '1.0',
        next_coefficient: '1.1',
        gold_to_upgrade: '1',
        curr_total_income: '0',
    });
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [lastOptimization, setLastOptimization] = useState(null);

    const api = `${import.meta.env.VITE_API_URL}/buildings`;

    const fetchBuildings = async () => {
        const res = await fetch(api);
        const data = await res.json();
        setBuildings(data);
    };

    const normalizeInput = (value) => {
        if (typeof value === 'string') {
            const num = parseFloat(value);
            if (value.toLowerCase().includes('k')) return num * 1_000;
            if (value.toLowerCase().includes('m')) return num * 1_000_000;
            if (value.toLowerCase().includes('b')) return num * 1_000_000_000;
            if (value.toLowerCase().includes('t')) return num * 1_000_000_000_000;
        }
        return value;
    };

    const displayToValue = (input) => {
        const num = parseFloat(input);
        if (input.toLowerCase().includes('k')) return num * 1_000;
        if (input.toLowerCase().includes('m')) return num * 1_000_000;
        if (input.toLowerCase().includes('b')) return num * 1_000_000_000;
        if (input.toLowerCase().includes('t')) return num * 1_000_000_000_000;
        return Number(input);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const method = editingId ? 'PATCH' : 'POST';
        const url = editingId ? `${api}/${editingId}` : api;

        const changes = {};
        Object.entries(form).forEach(([key, value]) => {
            if (!editingId || value !== initialForm[key]) {
                changes[key] =
                    key === 'name' ? value : isNaN(Number(value)) ? displayToValue(value) : Number(value);
            }
        });

        await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(changes),
        });

        setForm({ ...initialForm });
        setEditingId(null);
        fetchBuildings();
    };


    const handleCancelEdit = () => {
        setEditingId(null);
        setForm({ ...initialForm });
    };

    const initialForm = {
        name: '',
        curr_level: '1',
        num_employees: '1',
        curr_coefficient: '1.0',
        next_coefficient: '1.1',
        gold_to_upgrade: '1',
        curr_total_income: '0',
    };

    const handleEdit = (b) => {
        setForm(b);
        setEditingId(b.id);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this building?')) return;
        await fetch(`${api}/${id}`, { method: 'DELETE' });
        fetchBuildings();
    };

    const handleLevelUp = async (b) => {
        const payload = {
            curr_level: b.curr_level + 1,
            curr_coefficient: b.next_coefficient,
            next_coefficient: b.next_coefficient + 0.1,
        };

        await fetch(`${api}/${b.id}/levelup`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        fetchBuildings();
    };

    const filteredBuildings = buildings
        .filter((b) =>
            b.name.toLowerCase().includes(search.toLowerCase()) ||
            b.id.toString().includes(search)
        )
        .sort((a, b) => b.curr_total_income - a.curr_total_income);


    const saveOptimizationInput = (data) => {
        localStorage.setItem('lastOptimization', JSON.stringify(data));
        setLastOptimization(data);
    };

    const loadLastOptimization = () => {
        const stored = localStorage.getItem('lastOptimization');
        if (stored) setLastOptimization(JSON.parse(stored));
    };

    useEffect(() => {
        fetchBuildings();
        loadLastOptimization();
    }, []);

    return (
        <div className="p-4 max-w-5xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">Manage Buildings</h2>

            <Input
                type="text"
                placeholder="Search by name or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="mb-4"
            />

            <form onSubmit={handleSubmit}>
                <Card className="mb-6">
                    <CardContent className="p-4 grid grid-cols-2 gap-4">
                        {Object.entries(form).map(([key, value]) => (
                            <div key={key} className="flex flex-col">
                                <Label htmlFor={key}>{key.replace(/_/g, ' ')}</Label>
                                <Input
                                    name={key}
                                    value={value}
                                    onChange={handleChange}
                                    type="text"
                                />
                            </div>
                        ))}
                        <div className="col-span-2 flex gap-2">
                            <Button type="submit">
                                {editingId ? 'Update' : 'Create'} Building
                            </Button>
                            {editingId && (
                                <Button variant="secondary" onClick={handleCancelEdit} type="button">
                                    Cancel
                                </Button>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </form>

            <table className="w-full table-auto border">
                <thead>
                    <tr className="bg-gray-200">
                        <th className="p-2">ID</th>
                        <th className="p-2">Name</th>
                        <th className="p-2">Employees</th>
                        <th className="p-2">Level</th>
                        <th className="p-2">Income</th>
                        <th className="p-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredBuildings.map((b) => (
                        <tr key={b.id} className="border-t">
                            <td className="p-2">{b.id}</td>
                            <td className="p-2">{b.name}</td>
                            <td className="p-2">{b.num_employees}</td>
                            <td className="p-2">{b.curr_level}</td>
                            <td className="p-2">{b.curr_total_income}</td>
                            <td className="p-2 space-x-2">
                                <Button variant="outline" onClick={() => handleEdit(b)}>Edit</Button>
                                <Button variant="secondary" onClick={() => handleLevelUp(b)}>Level Up</Button>
                                <Button variant="destructive" onClick={() => handleDelete(b.id)}>Delete</Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {lastOptimization && (
                <div className="mt-6 p-4 bg-gray-100 rounded shadow">
                    <h3 className="font-semibold mb-2">Last Optimization Input:</h3>
                    <pre className="text-sm text-gray-700 bg-white p-2 rounded overflow-x-auto">
                        {JSON.stringify(lastOptimization, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
}
