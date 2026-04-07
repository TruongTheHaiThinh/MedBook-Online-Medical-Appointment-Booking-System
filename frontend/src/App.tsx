import { CalendarDays, Stethoscope } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <div className="text-center space-y-6 max-w-2xl px-4">
        <div className="inline-flex items-center justify-center p-4 bg-blue-100 rounded-full mb-4">
          <Stethoscope className="w-12 h-12 text-blue-600" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-cyan-500">
          MedBook Frontend
        </h1>
        <p className="text-lg text-slate-600">
          Hệ thống đặt lịch khám bệnh trực tuyến. Giao diện đang được phát triển.
        </p>
        <div className="pt-8">
          <button className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
            <CalendarDays className="w-5 h-5" />
            <span>Thử nghiệm</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
