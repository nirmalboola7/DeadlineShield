import { useEffect,useState } from 'react';
import { Routes,Route,Navigate,useLocation,useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Calendar from './pages/Calendar';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import { api } from './services/api';

function ProtectedLayout({user,onLogout,onUserUpdate}) {
  const location=useLocation();
  const title=({ '/':'Dashboard','/calendar':'Calendar','/analytics':'Analytics','/profile':'Profile'})[location.pathname]||'Workspace';
  return <div className="app-shell"><Sidebar user={user} onLogout={onLogout}/><main className="main-area"><Navbar title={title} user={user}/><Routes><Route path="/" element={<Dashboard/>}/><Route path="/calendar" element={<Calendar/>}/><Route path="/analytics" element={<Analytics/>}/><Route path="/profile" element={<Profile user={user} onUserUpdate={onUserUpdate}/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></main></div>;
}
export default function App(){
  const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('deadlineshield_user'));}catch{return null;}});
  const navigate=useNavigate();
  useEffect(()=>{if(user){api('/auth/me').then(r=>{setUser(r.user);localStorage.setItem('deadlineshield_user',JSON.stringify(r.user));}).catch(()=>{localStorage.removeItem('deadlineshield_token');localStorage.removeItem('deadlineshield_user');setUser(null);});}},[]);
  async function authenticate(path,form){const result=await api(path,{method:'POST',body:JSON.stringify(form)});localStorage.setItem('deadlineshield_token',result.token);localStorage.setItem('deadlineshield_user',JSON.stringify(result.user));setUser(result.user);navigate('/');}
  async function logout(){try{await api('/auth/logout',{method:'POST'});}catch{}localStorage.removeItem('deadlineshield_token');localStorage.removeItem('deadlineshield_user');setUser(null);navigate('/login');}
  function updateUser(next){setUser(next);localStorage.setItem('deadlineshield_user',JSON.stringify(next));}
  return user?<ProtectedLayout user={user} onLogout={logout} onUserUpdate={updateUser}/>:<Routes><Route path="/register" element={<Register onRegister={f=>authenticate('/auth/register',f)}/>}/><Route path="*" element={<Login onLogin={f=>authenticate('/auth/login',f)}/>}/></Routes>;
}
