import time

class Timer(object):
  TIMER_STOP = -1
  
  def init(self, duration):
      self._start_time = self.TIMER_STOP
      self._duration = duration
      
  # inicia el timer
  def start(self):
      if self._start_time == self.TIMER_STOP:
          self._start_time = time.time()
  
	# detiene el timer
  def stop(self):
      if self._start_time != self.TIMER_STOP:
          self._start_time = self.TIMER_STOP
          
  # dice si el timer esta corriendo
  def running(self):
      return self._start_time != self.TIMER_STOP
  
  # dice si el timer termino
  def timeout(self):
      if not self.running():
          return False
      
      else:
          return time.time() - self._start_time >= self._duration