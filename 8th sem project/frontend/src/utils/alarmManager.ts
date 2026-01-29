// Alarm sound utility for critical anomalies
export class AlarmManager {
  private static instance: AlarmManager;
  private audioContext: AudioContext | null = null;
  private isPlaying: boolean = false;

  private constructor() {
    if (typeof window !== 'undefined') {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
  }

  static getInstance(): AlarmManager {
    if (!AlarmManager.instance) {
      AlarmManager.instance = new AlarmManager();
    }
    return AlarmManager.instance;
  }

  playAlarm(priority: string): void {
    if (this.isPlaying || priority === 'LOW' || priority === 'MEDIUM') {
      return; // Only play for HIGH and CRITICAL
    }

    if (!this.audioContext) {
      console.warn('Audio context not available');
      return;
    }

    this.isPlaying = true;

    // Create oscillator for siren sound
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    // Configure based on priority
    if (priority === 'CRITICAL') {
      // Fast, high-pitched alarm
      oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(
        1200,
        this.audioContext.currentTime + 0.2
      );
      gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        this.audioContext.currentTime + 0.5
      );
    } else {
      // Medium alarm for HIGH priority
      oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(
        900,
        this.audioContext.currentTime + 0.3
      );
      gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        this.audioContext.currentTime + 0.4
      );
    }

    oscillator.type = 'sine';
    oscillator.start();
    oscillator.stop(this.audioContext.currentTime + 0.5);

    oscillator.onended = () => {
      this.isPlaying = false;
    };
  }

  playMultipleAlerts(priority: string, count: number = 3): void {
    let played = 0;
    const interval = setInterval(() => {
      if (played >= count) {
        clearInterval(interval);
        return;
      }
      this.playAlarm(priority);
      played++;
    }, 600);
  }
}

export const alarmManager = AlarmManager.getInstance();
