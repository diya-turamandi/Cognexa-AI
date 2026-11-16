
import { useState, useEffect, useRef } from "react";

import {
  LayoutDashboard,
  Files,
  MessageSquare,
  UploadCloud,
  Search,
  Bell,
  Plus,
  Sparkles,
  Clock3,
  HardDrive,
  ArrowUpRight,
  Menu,
  X,
  Send,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  LoaderCircle,
  ChevronRight,
  FileText,
  Trash2,
  BrainCircuit,
  ShieldCheck,
} from "lucide-react";

import { uploadDocument, checkBackend } from "./api";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "My Documents", icon: Files },
  { name: "AI Assistant", icon: MessageSquare },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState("");
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const fileInput = useRef(null);

  useEffect(() => {
    checkBackend()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  const handleUpload = async (file) => {
    if (!file) return;

    setError("");

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError("File size must be less than 15 MB.");
      return;
    }

    setUploading(true);

    try {
      const result = await uploadDocument(file);

      const newDocument = {
        ...result.document,
        extracted_text: result.extracted_text,
        pages: result.pages,
        uploadedAt: new Date().toLocaleDateString(),
      };

      setDocuments((previous) => [
        newDocument,
        ...previous,
      ]);

      setActivePage("My Documents");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Upload failed. Check your backend connection."
      );
    } finally {
      setUploading(false);

      if (fileInput.current) {
        fileInput.current.value = "";
      }
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files[0];

    handleUpload(file);
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = documents.reduce(
    (total, doc) => total + doc.page_count,
    0
  );

  const deleteDocument = (id) => {
    setDocuments((previous) =>
      previous.filter((doc) => doc.id !== id)
    );

    if (selectedDocument?.id === id) {
      setSelectedDocument(null);
    }
  };

  const renderDashboard = () => (
    <>
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-purple-600 mb-3">
          <Sparkles size={16} />
          YOUR PERSONAL KNOWLEDGE SPACE
        </div>

        <h1 className="text-3xl font-bold text-gray-900">
          Welcome to MindVault.
        </h1>

        <p className="text-gray-500 mt-2">
          Your knowledge, organized and ready to explore.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">

        <StatCard
          title="Total Documents"
          value={documents.length}
          icon={Files}
          color="purple"
          subtitle="Uploaded documents"
        />

        <StatCard
          title="Total Pages"
          value={totalPages}
          icon={BookOpen}
          color="blue"
          subtitle="Pages extracted"
        />

        <StatCard
          title="Storage Used"
          value={
            (documents.reduce(
              (total, doc) => total + doc.file_size,
              0
            ) / (1024 * 1024)).toFixed(2) + " MB"
          }
          icon={HardDrive}
          color="green"
          subtitle="Uploaded PDF files"
        />

        <StatCard
          title="AI Status"
          value="Coming Soon"
          icon={BrainCircuit}
          color="orange"
          subtitle="RAG engine upcoming"
        />

      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        <div className="xl:col-span-2 bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">

          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="font-bold text-lg">
                Upload your knowledge
              </h2>

              <p className="text-gray-400 text-sm mt-1">
                Add PDFs to your personal knowledge library.
              </p>
            </div>

            <div className="bg-purple-50 p-3 rounded-xl">
              <UploadCloud className="text-purple-600" />
            </div>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-purple-200 rounded-2xl bg-purple-50/40 p-10 text-center hover:border-purple-500 transition"
          >

            <div className="mx-auto w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-4">
              <UploadCloud
                size={30}
                className="text-purple-600"
              />
            </div>

            <h3 className="font-semibold text-gray-800">
              Drag and drop your PDF here
            </h3>

            <p className="text-gray-400 text-sm mt-2">
              Or browse files from your computer
            </p>

            <input
              type="file"
              accept=".pdf,application/pdf"
              ref={fileInput}
              className="hidden"
              onChange={(e) =>
                handleUpload(e.target.files[0])
              }
            />

            <button
              onClick={() => fileInput.current?.click()}
              disabled={uploading}
              className="mt-6 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-xl font-medium text-sm disabled:opacity-60"
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <LoaderCircle className="animate-spin" size={17} />
                  Processing PDF...
                </span>
              ) : (
                "Browse Files"
              )}
            </button>

            <p className="text-xs text-gray-400 mt-4">
              PDF format · Maximum 15 MB
            </p>

          </div>

          {error && (
            <div className="mt-4 flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
              <AlertCircle size={17} />
              {error}
            </div>
          )}

        </div>

        <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 rounded-2xl p-6 text-white flex flex-col justify-between">

          <div>
            <div className="bg-white/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
              <Sparkles size={25} />
            </div>

            <p className="text-purple-200 text-xs tracking-widest font-semibold">
              YOUR SECOND BRAIN
            </p>

            <h2 className="text-2xl font-bold mt-3 leading-snug">
              Turn documents into knowledge.
            </h2>

            <p className="text-purple-200 text-sm mt-4 leading-6">
              Soon, ask questions, discover connections
              and get intelligent answers directly from
              your documents.
            </p>
          </div>

          <div className="mt-8">
            <div className="flex items-center gap-2 text-sm text-purple-200">
              <ShieldCheck size={17} />
              Document-grounded AI coming soon
            </div>

            <button
              onClick={() => setActivePage("AI Assistant")}
              className="mt-5 flex items-center gap-2 bg-white text-purple-900 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-purple-100"
            >
              Explore AI Assistant
              <ArrowUpRight size={17} />
            </button>
          </div>

        </div>

      </div>

      <div className="mt-8 bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">

        <div className="flex justify-between items-center mb-5">
          <div>
            <h2 className="font-bold text-lg">
              Recent Documents
            </h2>

            <p className="text-sm text-gray-400 mt-1">
              Your latest uploads
            </p>
          </div>

          <button
            onClick={() => setActivePage("My Documents")}
            className="text-purple-600 text-sm font-semibold flex items-center gap-1"
          >
            View all <ChevronRight size={16} />
          </button>
        </div>

        {documents.length === 0 ? (
          <EmptyState
            title="No documents yet"
            description="Upload your first PDF to get started."
          />
        ) : (
          <DocumentList
            documents={documents.slice(0, 4)}
            onSelect={setSelectedDocument}
            onDelete={deleteDocument}
          />
        )}

      </div>
    </>
  );

  const renderDocuments = () => (
    <>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-5 mb-8">

        <div>
          <h1 className="text-3xl font-bold">
            My Documents
          </h1>

          <p className="text-gray-500 mt-2">
            Manage and explore your knowledge library.
          </p>
        </div>

        <button
          onClick={() => fileInput.current?.click()}
          disabled={uploading}
          className="bg-purple-600 text-white rounded-xl px-5 py-3 flex items-center justify-center gap-2"
        >
          <Plus size={18} />
          Upload Document
        </button>

      </div>

      <input
        ref={fileInput}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        onChange={(e) => handleUpload(e.target.files[0])}
      />

      {error && (
        <p className="text-red-600 bg-red-50 p-3 rounded-lg mb-4 text-sm">
          {error}
        </p>
      )}

      <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">

        <div className="relative mb-6">
          <Search
            className="absolute left-4 top-3.5 text-gray-400"
            size={19}
          />

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search your documents..."
            className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-3 outline-none focus:border-purple-400"
          />
        </div>

        {uploading && (
          <p className="text-purple-600 text-sm mb-4 flex items-center gap-2">
            <LoaderCircle size={16} className="animate-spin" />
            Processing document...
          </p>
        )}

        {filteredDocuments.length === 0 ? (
          <EmptyState
            title="No matching documents"
            description="Upload a PDF or try another search."
          />
        ) : (
          <DocumentList
            documents={filteredDocuments}
            onSelect={setSelectedDocument}
            onDelete={deleteDocument}
          />
        )}

      </div>
    </>
  );

  const renderAssistant = () => (
    <div className="max-w-3xl mx-auto text-center py-20">

      <div className="w-20 h-20 bg-purple-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <BrainCircuit size={38} className="text-purple-600" />
      </div>

      <span className="text-purple-600 font-semibold text-sm">
        NEXT DEVELOPMENT MILESTONE
      </span>

      <h1 className="text-3xl font-bold mt-4">
        Meet your AI Knowledge Assistant.
      </h1>

      <p className="text-gray-500 mt-4 leading-7">
        Your AI assistant will answer questions using
        your uploaded documents, provide source citations
        and retrieve relevant information.
      </p>

      <div className="bg-white rounded-2xl border border-gray-100 p-6 mt-8 text-left shadow-sm">

        <div className="flex items-center gap-3">
          <Sparkles className="text-purple-600" />
          <h3 className="font-semibold">
            Coming in the RAG milestone
          </h3>
        </div>

        <ul className="mt-5 space-y-4 text-sm text-gray-600">
          {[
            "Ask questions about uploaded PDFs",
            "Semantic document search",
            "Answers with page-level citations",
            "Conversation history",
            "Hybrid retrieval and reranking",
          ].map((item) => (
            <li key={item} className="flex items-center gap-3">
              <CheckCircle2
                size={17}
                className="text-purple-500"
              />
              {item}
            </li>
          ))}
        </ul>

      </div>

    </div>
  );

  return (
    <div className="min-h-screen flex">

      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
        />
      )}

      <aside className={`fixed lg:sticky top-0 left-0 z-50 w-64 h-screen bg-white border-r border-gray-100 flex flex-col transition-transform ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>

        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-purple-600 text-white w-10 h-10 rounded-xl flex items-center justify-center">
              <BrainCircuit size={24} />
            </div>

            <div>
              <h2 className="font-bold text-xl">
                Cognexa<span className="text-purple-600">.</span>
              </h2>

              <p className="text-xs text-gray-400">
                Your Second Brain
              </p>
            </div>
          </div>

          <button
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X />
          </button>
        </div>

        <div className="px-4 mt-5">
          <p className="text-xs text-gray-400 font-semibold tracking-widest px-3 mb-4">
            WORKSPACE
          </p>

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                onClick={() => {
                  setActivePage(item.name);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-2 text-sm font-medium transition ${activePage === item.name
                    ? "bg-purple-50 text-purple-700"
                    : "text-gray-500 hover:bg-gray-50"
                  }`}
              >
                <Icon size={19} />
                {item.name}
              </button>
            );
          })}
        </div>

        <div className="mt-auto p-5">
          <div className="bg-purple-50 rounded-2xl p-4">
            <Sparkles className="text-purple-600 mb-3" size={20} />

            <h3 className="font-semibold text-sm">
              Keep learning.
            </h3>

            <p className="text-xs text-gray-500 mt-2 leading-5">
              Your personal knowledge base is growing.
            </p>
          </div>

          <div className="mt-5 text-xs text-gray-400 text-center">
            COGNEXA AI · VERSION 1.0
          </div>
        </div>

      </aside>

      <main className="flex-1 min-w-0">

        <header className="h-20 bg-white border-b border-gray-100 flex items-center justify-between px-5 md:px-8 sticky top-0 z-30">

          <div className="flex items-center gap-4">
            <button
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu />
            </button>

            <div>
              <p className="text-sm font-semibold">
                {activePage}
              </p>

              <p className="text-xs text-gray-400">
                Cognexa AI Workspace
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">

            <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500">
              <span className={`w-2 h-2 rounded-full ${backendOnline ? "bg-green-500" : "bg-red-400"}`} />

              {backendOnline ? "Backend connected" : "Backend offline"}
            </div>

            <button className="relative p-2 text-gray-500 hover:bg-gray-50 rounded-xl">
              <Bell size={20} />
            </button>

            <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
              D
            </div>

          </div>

        </header>

        <div className="p-5 md:p-8 max-w-[1500px] mx-auto">

          {activePage === "Dashboard" && renderDashboard()}

          {activePage === "My Documents" && renderDocuments()}

          {activePage === "AI Assistant" && renderAssistant()}

        </div>

      </main>

      {selectedDocument && (
        <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4">

          <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col">

            <div className="p-5 border-b flex items-center justify-between">
              <div>
                <h2 className="font-bold">
                  {selectedDocument.filename}
                </h2>

                <p className="text-xs text-gray-400 mt-1">
                  {selectedDocument.page_count} pages
                </p>
              </div>

              <button
                onClick={() => setSelectedDocument(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X />
              </button>
            </div>

            <div className="p-6 overflow-y-auto whitespace-pre-wrap text-sm leading-7 text-gray-700">
              {selectedDocument.extracted_text || "No extracted text."}
            </div>

          </div>

        </div>
      )}

    </div>
  );
}

function StatCard({ title, value, icon: Icon, color, subtitle }) {
  const colors = {
    purple: "bg-purple-100 text-purple-600",
    blue: "bg-blue-100 text-blue-600",
    green: "bg-green-100 text-green-600",
    orange: "bg-orange-100 text-orange-600",
  };

  return (
    <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">

      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon size={21} />
        </div>

        <ArrowUpRight size={18} className="text-gray-300" />
      </div>

      <h3 className="text-2xl font-bold mt-5">
        {value}
      </h3>

      <p className="font-medium text-sm mt-1">
        {title}
      </p>

      <p className="text-xs text-gray-400 mt-2">
        {subtitle}
      </p>

    </div>
  );
}

function EmptyState({ title, description }) {
  return (
    <div className="text-center py-12">
      <div className="w-14 h-14 bg-purple-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <FileText className="text-purple-400" size={25} />
      </div>

      <h3 className="font-semibold text-gray-700">
        {title}
      </h3>

      <p className="text-sm text-gray-400 mt-2">
        {description}
      </p>
    </div>
  );
}

function DocumentList({ documents, onSelect, onDelete }) {
  return (
    <div className="divide-y divide-gray-100">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="py-4 flex items-center justify-between gap-3"
        >

          <button
            onClick={() => onSelect(doc)}
            className="flex items-center gap-4 min-w-0 text-left"
          >
            <div className="bg-red-50 p-3 rounded-xl">
              <FileText className="text-red-500" size={22} />
            </div>

            <div className="min-w-0">
              <h3 className="font-semibold text-sm truncate">
                {doc.filename}
              </h3>

              <p className="text-xs text-gray-400 mt-1">
                {doc.page_count} pages · {doc.uploadedAt}
              </p>
            </div>
          </button>

          <div className="flex items-center gap-3 shrink-0">
            <span className="hidden sm:flex text-xs text-green-600 items-center gap-1">
              <CheckCircle2 size={14} />
              Processed
            </span>

            <button
              onClick={() => onDelete(doc.id)}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
              title="Remove from this session"
            >
              <Trash2 size={17} />
            </button>
          </div>

        </div>
      ))}
    </div>
  );
}

export default App;
