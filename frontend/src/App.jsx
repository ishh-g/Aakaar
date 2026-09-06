import React, { useState, useEffect, useRef } from 'react';
import LoginScreen from './components/LoginScreen';
import CesiumGlobe from './components/CesiumGlobe';
import Header from './components/Header';
import PropertyDetailPanel from './components/PropertyDetailPanel';
import StatsSummaryBar from './components/StatsSummaryBar';
import LegendPanel from './components/LegendPanel';
import ConflictsDashboard from './components/ConflictsDashboard';
import ReportsPage from './components/ReportsPage';
import UlpinGeneratorPage from './components/UlpinGeneratorPage';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = sessionStorage.getItem('ulpin_auth_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('map'); // 'map' | 'conflicts'
  const [mapData, setMapData] = useState(null);
  const [conflicts, setConflicts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [backendStatus, setBackendStatus] = useState('Connecting...');
  const viewerInstanceRef = useRef(null);

  // Fetch all map data, conflicts, and summary analytics
  const fetchAllData = async () => {
    try {
      const [healthRes, tilesRes, conflictsRes, summaryRes] = await Promise.all([
        fetch('http://localhost:8000/health').then(r => r.json()),
        fetch('http://localhost:8000/map/tiles').then(r => r.json()),
        fetch('http://localhost:8000/properties/conflicts').then(r => r.json()),
        fetch('http://localhost:8000/reports/summary').then(r => r.json())
      ]);

      if (healthRes.status === 'ok') {
        setBackendStatus('Connected');
      }
      setMapData(tilesRes);
      setConflicts(conflictsRes);
      setSummary(summaryRes);
    } catch (err) {
      console.error('Error fetching data:', err);
      setBackendStatus('Backend Offline');
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchAllData();
    }
  }, [currentUser]);

  // Handle Login Success
  const handleLoginSuccess = (authData) => {
    setCurrentUser(authData);
    sessionStorage.setItem('ulpin_auth_user', JSON.stringify(authData));
  };

  // Handle Logout
  const handleLogout = () => {
    setCurrentUser(null);
    setSelectedProperty(null);
    sessionStorage.removeItem('ulpin_auth_user');
  };

  // Extract all property records from mapData for SearchBar
  const propertiesList = React.useMemo(() => {
    if (!mapData || !mapData.features) return [];
    return mapData.features
      .filter((f) => f.properties?.layer === 'property')
      .map((f) => f.properties);
  }, [mapData]);

  // Handle officer manual verification
  const handleVerifyProperty = async (propertyId) => {
    if (!currentUser || !currentUser.access_token) return;

    try {
      const verifyRes = await fetch(`http://localhost:8000/properties/${propertyId}/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${currentUser.access_token}`
        }
      }).then(r => r.json());

      if (verifyRes.status === 'success') {
        await fetchAllData();
        if (selectedProperty && selectedProperty.property_id === propertyId) {
          setSelectedProperty(prev => prev ? { ...prev, verification_status: 'verified' } : null);
        }
      }
    } catch (err) {
      console.error('Verification failed:', err);
    }
  };

  // Inspect property from Dashboard on 3D Map
  const handleInspectProperty = (propertyId) => {
    const prop = propertiesList.find(p => p.property_id === propertyId);
    if (prop) {
      setSelectedProperty(prop);
      setActiveTab('map');
    }
  };

  // If not logged in, show Login Screen
  if (!currentUser) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        conflictsCount={conflicts.length}
        propertiesList={propertiesList}
        onSelectProperty={(prop) => {
          setSelectedProperty(prop);
          if (activeTab !== 'map') {
            setActiveTab('map');
          }
        }}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <main className="app-main">
        {activeTab === 'map' && (
          <div className="map-view-container">
            <CesiumGlobe
              mapData={mapData}
              conflicts={conflicts}
              selectedProperty={selectedProperty}
              onSelectProperty={(prop) => setSelectedProperty(prop)}
              viewerInstanceRef={viewerInstanceRef}
            />

            <StatsSummaryBar summary={summary} />

            <LegendPanel />

            {selectedProperty && (
              <PropertyDetailPanel
                property={selectedProperty}
                conflicts={conflicts}
                user={currentUser}
                onClose={() => setSelectedProperty(null)}
                onVerify={handleVerifyProperty}
              />
            )}
          </div>
        )}

        {activeTab === 'conflicts' && (
          <ConflictsDashboard
            conflicts={conflicts}
            user={currentUser}
            onVerify={handleVerifyProperty}
            onInspectProperty={handleInspectProperty}
          />
        )}

        {activeTab === 'reports' && (
          <ReportsPage
            summary={summary}
            onRefresh={fetchAllData}
          />
        )}

        {activeTab === 'generator' && (
          <UlpinGeneratorPage
            mapData={mapData}
            propertiesList={propertiesList}
            onInspectProperty={handleInspectProperty}
          />
        )}
      </main>
    </div>
  );
}
