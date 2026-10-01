import { useEffect,useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client.js';
import { Alert,EmptyState,Spinner } from '../components/ui.jsx';

export default function Notifications(){
 const [items,setItems]=useState(null); const [error,setError]=useState(null);
 const load=()=>api.get('/notifications/').then(r=>setItems(r.data)).catch(e=>setError(e.response?.data?.detail||'Could not load notifications.'));
 useEffect(()=>{load()},[]);
 const read=async id=>{await api.post(`/notifications/${id}/read/`);setItems(items.map(n=>n.id===id?{...n,is_read:true}:n))};
 const readAll=async()=>{await api.post('/notifications/read-all/');setItems(items.map(n=>({...n,is_read:true})))};
 if(error)return <Alert>{error}</Alert>; if(!items)return <Spinner/>;
 return <div className="space-y-5"><div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold">Notifications</h1><p className="text-sm text-slate-500">Matching jobs and marketplace updates.</p></div>{items.some(n=>!n.is_read)&&<button className="btn btn-outline" onClick={readAll}>Mark all read</button>}</div>{items.length===0?<EmptyState title="No notifications yet" text="When a new job matches your profile, you will see it here."/>:<div className="space-y-3">{items.map(n=><div key={n.id} className={`card p-4 ${!n.is_read?'border-indigo-200 bg-indigo-50/40':''}`}><div className="flex gap-3"><div className="flex-1"><p className="font-medium text-slate-900">{n.message}</p><p className="mt-1 text-xs text-slate-500">{new Date(n.created_at).toLocaleString()}</p>{n.link&&<Link className="mt-2 inline-block text-sm font-semibold text-indigo-600" to={n.link}>View job</Link>}</div>{!n.is_read&&<button className="text-xs font-semibold text-indigo-600" onClick={()=>read(n.id)}>Mark read</button>}</div></div>)}</div>}</div>
}
