import React, { useEffect, useRef } from 'react';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

export default function CesiumGlobe({ 
  mapData, 
  conflicts, 
  selectedProperty, 
  onSelectProperty,
  viewerInstanceRef 
}) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const propertyEntitiesRef = useRef(new Map());

  // BVCOE Paschim Vihar, Delhi geospatial center
  const BVCOE_LON = 77.1130;
  const BVCOE_LAT = 28.6773;

  useEffect(() => {
    if (!containerRef.current) return;

    // 1. Initialize Cesium Viewer
    const viewer = new Cesium.Viewer(containerRef.current, {
      timeline: false,
      animation: false,
      sceneModePicker: false,
      baseLayerPicker: false,
      geocoder: false,
      navigationHelpButton: false,
      fullscreenButton: false,
      homeButton: false,
      infoBox: false,
      selectionIndicator: false,
    });

    // Darker / sharper atmospheric rendering
    viewer.scene.globe.enableLighting = false;
    viewer.scene.globe.depthTestAgainstTerrain = false;

    // Fly camera directly to BVCOE coordinates at oblique 3D angle
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(BVCOE_LON, BVCOE_LAT - 0.0018, 380),
      orientation: {
        heading: Cesium.Math.toRadians(0.0),
        pitch: Cesium.Math.toRadians(-42.0),
        roll: 0.0
      },
      duration: 1.5
    });

    viewerRef.current = viewer;
    if (viewerInstanceRef) {
      viewerInstanceRef.current = viewer;
    }

    // 2. Click Handler to pick 3D Property Volume
    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((movement) => {
      const pickedObject = viewer.scene.pick(movement.position);
      if (Cesium.defined(pickedObject) && pickedObject.id) {
        const entity = pickedObject.id;
        const propData = entity.propertyData;
        if (propData) {
          onSelectProperty(propData);
        }
      } else {
        onSelectProperty(null);
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    return () => {
      handler.destroy();
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  // 3. Render Layers when mapData updates
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !mapData || !mapData.features) return;

    viewer.entities.removeAll();
    propertyEntitiesRef.current.clear();

    mapData.features.forEach((feature) => {
      const { geometry, properties } = feature;
      if (!geometry || !geometry.coordinates) return;

      const layer = properties.layer;

      // A. 2D Parcel Boundary Lines
      if (layer === 'parcel') {
        const coords = geometry.coordinates[0];
        const flatCoords = coords.flat();
        viewer.entities.add({
          name: `Parcel ${properties.ulpin_2d}`,
          polygon: {
            hierarchy: Cesium.Cartesian3.fromDegreesArray(flatCoords),
            material: Cesium.Color.CYAN.withAlpha(0.08),
            outline: true,
            outlineColor: Cesium.Color.CYAN.withAlpha(0.85),
            outlineWidth: 3,
            height: 0.2
          }
        });
      }

      // B. 3D Extruded Property Volumes
      if (layer === 'property') {
        const coords = geometry.coordinates[0];
        const flatCoords = coords.flat();
        const status = properties.verification_status;

        // Color coding by verification_status:
        // verified -> Green, conflict -> Red, unverified -> Gray
        let materialColor;
        let outlineColor;
        if (status === 'conflict') {
          materialColor = Cesium.Color.fromCssColorString('#ef4444').withAlpha(0.85); // Bright Red
          outlineColor = Cesium.Color.WHITE.withAlpha(0.95);
        } else if (status === 'verified') {
          materialColor = Cesium.Color.fromCssColorString('#22c55e').withAlpha(0.75); // Vibrant Green
          outlineColor = Cesium.Color.WHITE.withAlpha(0.85);
        } else {
          materialColor = Cesium.Color.fromCssColorString('#9ca3af').withAlpha(0.65); // Gray
          outlineColor = Cesium.Color.WHITE.withAlpha(0.7);
        }

        const entity = viewer.entities.add({
          name: properties.ulpin_3d,
          polygon: {
            hierarchy: Cesium.Cartesian3.fromDegreesArray(flatCoords),
            height: properties.elevation_min_m,
            extrudedHeight: properties.elevation_max_m,
            material: materialColor,
            outline: true,
            outlineColor: outlineColor,
            outlineWidth: 2,
            closeTop: true,
            closeBottom: true
          }
        });

        entity.propertyData = properties;
        propertyEntitiesRef.current.set(properties.property_id, entity);
      }
    });
  }, [mapData]);

  // 4. Handle Selected Property Highlighting & Camera Zoom
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !selectedProperty) return;

    const entity = propertyEntitiesRef.current.get(selectedProperty.property_id);
    if (entity) {
      viewer.flyTo(entity, {
        offset: new Cesium.HeadingPitchRange(
          Cesium.Math.toRadians(15.0),
          Cesium.Math.toRadians(-35.0),
          120
        ),
        duration: 1.2
      });
    }
  }, [selectedProperty]);

  return (
    <div 
      ref={containerRef} 
      className="cesium-wrapper"
      id="cesiumContainer"
    />
  );
}
