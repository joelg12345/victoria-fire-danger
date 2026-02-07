class VicFireDangerCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error('Please define an entity');
    this.config = config;
  }

  getCardSize() {
    return 10; 
  }

  set hass(hass) {
    const entityId = this.config.entity;
    const entity = hass.states[entityId];
    if (!entity) return;

    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    const baseId = entityId.replace('_rating_today', '');
    const rating = entity.state || 'UNKNOWN';
    const areaName = entity.attributes.area_name || 'District';
    const lastUpdated = entity.attributes.last_updated;

    const tobanToday = hass.states[`${baseId}_total_fire_ban_today`]?.state || 'No';
    const ratingTomorrow = hass.states[`${baseId}_rating_tomorrow`]?.state || 'UNKNOWN';
    const ratingDay3 = hass.states[`${baseId}_rating_day_3`]?.state || 'UNKNOWN';
    const ratingDay4 = hass.states[`${baseId}_rating_day_4`]?.state || 'UNKNOWN';
    const tobanTomorrow = hass.states[`${baseId}_total_fire_ban_tomorrow`]?.state || 'No';
    const tobanDay3 = hass.states[`${baseId}_total_fire_ban_day_3`]?.state || 'No';
    const tobanDay4 = hass.states[`${baseId}_total_fire_ban_day_4`]?.state || 'No';

    const ratingInfo = this.getRatingInfo(rating);
    const needleAngle = this.getNeedleAngle(rating);
    const hasBan = tobanToday === 'Yes';

    const COLORS = { MODERATE: '#71b94b', HIGH: '#fef200', EXTREME: '#f59330', CATASTROPHIC: '#ce161e' };
    
    const banSvg = `<svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12.3304 26.5739C8.1986 24.2452 7.11077 22.0411 7.73271 19.0307C8.19186 16.8078 9.6953 14.9993 9.83946 12.7807C10.4817 13.9494 10.75 14.7921 10.8218 16.0134C12.8644 13.5109 14.2142 10.0464 14.2941 6.40723C14.2941 6.40723 19.6143 9.53323 19.9634 14.2551C20.4214 13.2818 20.652 11.7361 20.194 10.7343C21.568 11.7361 29.61 20.63 19.1047 26.5739C21.0798 22.7281 19.6142 17.539 16.1849 15.1425C16.4139 16.173 16.0124 20.0164 14.4952 21.7053C14.9156 18.8834 14.0953 17.6901 14.0953 17.6901C14.0953 17.6901 13.8137 19.2708 12.7213 20.8675C11.7237 22.3256 11.0325 23.8731 12.3304 26.5739Z" fill="currentColor"></path><path d="M24.8596 28.057L25.2132 28.4105L25.5668 28.057L27.6881 25.9357L28.0416 25.5821L27.6881 25.2286L6.47487 4.01536L6.12132 3.66181L5.76777 4.01536L3.64645 6.13668L3.29289 6.49023L3.64645 6.84379L24.8596 28.057Z" fill="#DB4433" stroke="var(--ha-card-background, var(--card-background-color, white))" stroke-width="0.5"></path><circle cx="16" cy="16.4902" r="14.5" stroke="#DB4433" stroke-width="3"></circle></svg>`;

    const getDayName = (offset) => {
      const d = lastUpdated ? new Date(lastUpdated) : new Date();
      d.setDate(d.getDate() + offset);
      return d.toLocaleDateString('en-AU', { weekday: 'long' });
    };

    this.shadowRoot.innerHTML = `
      <style>
        :host { 
          display: block; 
          min-height: 485px; 
          contain: layout;
        }
        ha-card { 
          display: flex;
          flex-direction: column;
          overflow: hidden; 
          padding: 16px; 
          text-align: center; 
          color: var(--primary-text-color); 
          background: var(--ha-card-background, var(--card-background-color, white)); 
          min-height: 485px;
          box-sizing: border-box;
        }
        .header-title { font-size: 22px; font-weight: 800; color: var(--primary-text-color); }
        .header-date { font-size: 14px; color: var(--secondary-text-color); margin-bottom: 20px; }
        
        .gauge-container { width: 260px; height: 140px; margin: 0 auto; position: relative; flex-shrink: 0; }
        .needle-pivot { transition: transform 1.5s ease-in-out; transform-origin: 130px 130px; transform: rotate(${needleAngle}deg); }
        
        .rating-box { 
          background: ${ratingInfo.color}; 
          color: #212121 !important; 
          padding: 8px 30px; 
          font-size: 24px; 
          font-weight: 900; 
          border: 2px solid #212121; 
          margin: 16px auto; 
          display: inline-block; 
          text-transform: uppercase; 
          flex-shrink: 0;
        }
        
        .rating-message { font-size: 18px; font-weight: 700; margin: 16px 0; max-width: 300px; margin-left: auto; margin-right: auto; line-height: 1.2; color: var(--primary-text-color); flex-shrink: 0; }
        
        .ban-section { display: ${hasBan ? 'flex' : 'none'}; align-items: center; justify-content: center; margin-top: 10px; flex-shrink: 0; }
        .ban-label { font-size: 20px; font-weight: 800; color: #DB4433; margin-left: 12px; }
        
        .spacer { flex-grow: 1; }

        .forecast-grid { display: flex; gap: 8px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--divider-color); flex-shrink: 0; }
        
        .forecast-item { 
          flex: 1; 
          background: var(--secondary-background-color); 
          border-radius: 10px; 
          padding: 10px 4px; 
          display: flex; 
          flex-direction: column; 
          align-items: center; 
          border: 1px solid var(--divider-color); 
        }
        
        .fc-day { font-size: 11px; font-weight: 700; color: var(--secondary-text-color); margin-bottom: 6px; }
        
        .fc-rating-tag { 
          font-weight: 900; 
          padding: 4px 0; 
          border-radius: 4px; 
          width: 90%; 
          text-align: center; 
          font-size: 10px; 
          border: 1px solid rgba(0,0,0,0.1); 
          color: #212121 !important;
        }
        
        .fc-ban-badge { font-size: 8px; font-weight: 950; padding: 2px 6px; margin-top: 4px; color: var(--secondary-text-color); opacity: 0.3; }
        .fc-ban-badge.active { color: #ce161e; opacity: 1; background: rgba(206, 22, 30, 0.1); border: 1px solid #ce161e; border-radius: 4px; }
      </style>
      <ha-card>
        <div class="header-title">${areaName}</div>
        <div class="header-date">${lastUpdated ? new Date(lastUpdated).toLocaleDateString('en-AU', {weekday:'long', day:'numeric', month:'long'}) : 'Today'}</div>
        <div class="gauge-container">
          <svg viewBox="0 0 260 140">
            <path d="M 30 130 A 100 100 0 0 1 59.3 59.3 L 130 130 Z" fill="${COLORS.MODERATE}" stroke="#212121"/>
            <path d="M 59.3 59.3 A 100 100 0 0 1 130 30 L 130 130 Z" fill="${COLORS.HIGH}" stroke="#212121"/>
            <path d="M 130 30 A 100 100 0 0 1 200.7 59.3 L 130 130 Z" fill="${COLORS.EXTREME}" stroke="#212121"/>
            <path d="M 200.7 59.3 A 100 100 0 0 1 230 130 L 130 130 Z" fill="${COLORS.CATASTROPHIC}" stroke="#212121"/>
            <g class="needle-pivot">
              <path d="M 130 130 L 126 120 L 130 40 L 134 120 Z" fill="var(--primary-text-color)" stroke="var(--ha-card-background, var(--card-background-color, white))"/>
              <circle cx="130" cy="130" r="10" fill="var(--primary-text-color)" stroke="var(--ha-card-background, var(--card-background-color, white))"/>
            </g>
          </svg>
        </div>
        <div class="rating-box">${rating}</div>
        <div class="rating-message">${ratingInfo.message}</div>
        <div class="ban-section">
          <div class="ban-logo">${banSvg}</div>
          <div class="ban-label">Total Fire Ban</div>
        </div>
        <div class="spacer"></div>
        <div class="forecast-grid">
          ${this.createForecastItem('Tomorrow', ratingTomorrow, tobanTomorrow)}
          ${this.createForecastItem(getDayName(2), ratingDay3, tobanDay3)}
          ${this.createForecastItem(getDayName(3), ratingDay4, tobanDay4)}
        </div>
      </ha-card>
    `;
  }

  createForecastItem(day, rating, toban) {
    const info = this.getRatingInfo(rating);
    const isBan = toban === 'Yes';

    return `
      <div class="forecast-item">
        <div class="fc-day">${day}</div>
        <div class="fc-rating-tag" style="background: ${info.color};">
          ${rating === 'NO RATING' ? 'NONE' : rating}
        </div>
        <div class="fc-ban-badge ${isBan ? 'active' : ''}">${isBan ? 'FIRE BAN' : 'NO BAN'}</div>
      </div>`;
  }

  getNeedleAngle(rating) {
    const angles = { 'MODERATE': -67.5, 'HIGH': -22.5, 'EXTREME': 22.5, 'CATASTROPHIC': 67.5 };
    return angles[rating] || -90;
  }

  getRatingInfo(rating) {
    const ratings = {
      'MODERATE': { color: '#71b94b', message: 'Plan and prepare' },
      'HIGH': { color: '#fef200', message: 'Be ready to act' },
      'EXTREME': { color: '#f59330', message: 'Take action now to protect your life and property' },
      'CATASTROPHIC': { color: '#ce161e', message: 'For your survival, leave bush fire risk areas' },
      'NO RATING': { color: '#ffffff', message: 'No rating issued' }
    };
    return ratings[rating] || { color: '#ffffff', message: 'Check local conditions' };
  }
}

if (!customElements.get('vic-fire-danger-card')) {
  customElements.define('vic-fire-danger-card', VicFireDangerCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: 'vic-fire-danger-card',
    name: 'Victoria Fire Danger Card',
    description: 'A theme-aware gauge and forecast card for Victorian CFA districts.',
    preview: true
  });
}

console.info(
  '%c VIC-FIRE-DANGER-CARD %c Version 1.1.1 ',
  'color: white; background: #ce161e; font-weight: 700;',
  'color: #ce161e; background: white; font-weight: 700;'
);
