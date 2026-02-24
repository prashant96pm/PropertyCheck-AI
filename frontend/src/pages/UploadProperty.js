import React, { useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import FloatingActionButton from '../components/FloatingActionButton';
import { 
  Upload, 
  FileText, 
  Loader2, 
  CheckCircle2, 
  ArrowLeft,
  X,
  AlertCircle,
  Sparkles,
  Building2
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
  "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const DOC_TYPES = [
  { value: "sale_deed", label: "Sale Deed" },
  { value: "mother_deed", label: "Mother Deed" },
  { value: "ec_certificate", label: "Encumbrance Certificate (EC)" },
  { value: "rtc_pahani", label: "RTC / Pahani" },
  { value: "7_12_extract", label: "7/12 Extract" },
  { value: "khata_certificate", label: "Khata Certificate" },
  { value: "mutation_record", label: "Mutation Record" },
  { value: "other", label: "Other Document" }
];

const UploadProperty = () => {
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [propertyId, setPropertyId] = useState(null);
  
  const [propertyForm, setPropertyForm] = useState({
    survey_no: '',
    khata_no: '',
    state: '',
    district: '',
    taluk: '',
    village: '',
    address: ''
  });
  
  const [documents, setDocuments] = useState([]);
  const [currentDocType, setCurrentDocType] = useState('sale_deed');
  const [uploadingDoc, setUploadingDoc] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach(file => {
      setDocuments(prev => [...prev, {
        file,
        type: currentDocType,
        status: 'pending',
        name: file.name
      }]);
    });
  }, [currentDocType]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    },
    maxSize: 20 * 1024 * 1024
  });

  const handlePropertySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/properties`, propertyForm, {
        withCredentials: true
      });
      setPropertyId(response.data.property_id);
      setStep(2);
      toast.success('Property created successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create property');
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (doc, index) => {
    if (!propertyId) return;
    
    setDocuments(prev => prev.map((d, i) => 
      i === index ? { ...d, status: 'uploading' } : d
    ));

    const formData = new FormData();
    formData.append('file', doc.file);

    try {
      const response = await axios.post(
        `${API}/documents/upload?property_id=${propertyId}&doc_type=${doc.type}`,
        formData,
        {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      setDocuments(prev => prev.map((d, i) => 
        i === index ? { 
          ...d, 
          status: 'uploaded', 
          documentId: response.data.document_id,
          ocrText: response.data.ocr_text,
          extractedData: response.data.extracted_data
        } : d
      ));
      
      toast.success(`${doc.name} uploaded and processed`);
    } catch (error) {
      setDocuments(prev => prev.map((d, i) => 
        i === index ? { ...d, status: 'error' } : d
      ));
      toast.error(`Failed to upload ${doc.name}`);
    }
  };

  const uploadAllDocuments = async () => {
    setUploadingDoc(true);
    
    for (let i = 0; i < documents.length; i++) {
      if (documents[i].status === 'pending') {
        await uploadDocument(documents[i], i);
      }
    }
    
    setUploadingDoc(false);
  };

  const removeDocument = (index) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  const proceedToAnalysis = () => {
    navigate(`/property/${propertyId}`);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/dashboard" className="flex items-center gap-2">
              <ArrowLeft className="h-5 w-5 text-slate-400" />
              <Building2 className="h-8 w-8 text-cyan-400" />
              <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center">
            <div className={`h-10 w-10 rounded-full flex items-center justify-center font-medium transition-all duration-300 ${
              step >= 1 ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30' : 'bg-slate-700 text-slate-400'
            }`}>
              1
            </div>
            <div className={`w-24 h-1 transition-all duration-300 ${step >= 2 ? 'bg-cyan-500' : 'bg-slate-700'}`} />
            <div className={`h-10 w-10 rounded-full flex items-center justify-center font-medium transition-all duration-300 ${
              step >= 2 ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30' : 'bg-slate-700 text-slate-400'
            }`}>
              2
            </div>
          </div>
        </div>

        {/* Step 1: Property Details */}
        {step === 1 && (
          <div className="glass-card">
            <div className="mb-6">
              <h1 className="text-2xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                Property Details
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Enter the basic details of the property you want to verify
              </p>
            </div>
            
            <form onSubmit={handlePropertySubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="survey_no" className="text-slate-300">Survey Number *</Label>
                  <Input
                    id="survey_no"
                    data-testid="survey-no-input"
                    value={propertyForm.survey_no}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, survey_no: e.target.value }))}
                    placeholder="e.g., 123/4"
                    className="input-glass"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="khata_no" className="text-slate-300">Khata Number</Label>
                  <Input
                    id="khata_no"
                    data-testid="khata-no-input"
                    value={propertyForm.khata_no}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, khata_no: e.target.value }))}
                    placeholder="e.g., KH-123"
                    className="input-glass"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="state" className="text-slate-300">State *</Label>
                  <Select 
                    value={propertyForm.state}
                    onValueChange={(value) => setPropertyForm(prev => ({ ...prev, state: value }))}
                  >
                    <SelectTrigger data-testid="state-select" className="input-glass">
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {INDIAN_STATES.map(state => (
                        <SelectItem key={state} value={state} className="text-slate-300 hover:bg-slate-800">
                          {state}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="district" className="text-slate-300">District *</Label>
                  <Input
                    id="district"
                    data-testid="district-input"
                    value={propertyForm.district}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, district: e.target.value }))}
                    placeholder="e.g., Bengaluru Urban"
                    className="input-glass"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="taluk" className="text-slate-300">Taluk</Label>
                  <Input
                    id="taluk"
                    data-testid="taluk-input"
                    value={propertyForm.taluk}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, taluk: e.target.value }))}
                    placeholder="e.g., Anekal"
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="village" className="text-slate-300">Village</Label>
                  <Input
                    id="village"
                    data-testid="village-input"
                    value={propertyForm.village}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, village: e.target.value }))}
                    placeholder="e.g., Sarjapur"
                    className="input-glass"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="address" className="text-slate-300">Full Address</Label>
                <Input
                  id="address"
                  data-testid="address-input"
                  value={propertyForm.address}
                  onChange={(e) => setPropertyForm(prev => ({ ...prev, address: e.target.value }))}
                  placeholder="Complete property address"
                  className="input-glass"
                />
              </div>

              <Button 
                data-testid="submit-property-btn"
                type="submit" 
                className="w-full btn-primary"
                disabled={loading || !propertyForm.survey_no || !propertyForm.state || !propertyForm.district}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Property...
                  </>
                ) : (
                  'Continue to Document Upload'
                )}
              </Button>
            </form>
          </div>
        )}

        {/* Step 2: Document Upload */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="glass-card">
              <div className="mb-6">
                <h1 className="text-2xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  Upload Documents
                </h1>
                <p className="text-slate-400 text-sm mt-1">
                  Upload property documents for AI-powered OCR and analysis
                </p>
              </div>
              
              <div className="space-y-6">
                {/* Document Type Selection */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Document Type</Label>
                  <Select value={currentDocType} onValueChange={setCurrentDocType}>
                    <SelectTrigger data-testid="doc-type-select" className="input-glass">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {DOC_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value} className="text-slate-300 hover:bg-slate-800">
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Dropzone */}
                <div
                  {...getRootProps()}
                  data-testid="document-dropzone"
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300 ${
                    isDragActive 
                      ? 'border-cyan-500 bg-cyan-500/10' 
                      : 'border-slate-600 hover:border-cyan-500/50 hover:bg-slate-800/50'
                  }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="h-12 w-12 text-slate-500 mx-auto mb-4" />
                  {isDragActive ? (
                    <p className="text-cyan-400">Drop files here...</p>
                  ) : (
                    <>
                      <p className="text-slate-400 mb-2">
                        Drag & drop documents here, or click to browse
                      </p>
                      <p className="text-xs text-slate-500">
                        Supports PDF, PNG, JPG, TIFF (max 20MB)
                      </p>
                    </>
                  )}
                </div>

                {/* Document List */}
                {documents.length > 0 && (
                  <div className="space-y-3">
                    <Label className="text-slate-300">Queued Documents</Label>
                    {documents.map((doc, index) => (
                      <div 
                        key={index}
                        className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-cyan-400" />
                          <div>
                            <p className="text-sm font-medium text-white">{doc.name}</p>
                            <p className="text-xs text-slate-500">
                              {DOC_TYPES.find(t => t.value === doc.type)?.label}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {doc.status === 'pending' && (
                            <span className="text-xs text-slate-500">Pending</span>
                          )}
                          {doc.status === 'uploading' && (
                            <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
                          )}
                          {doc.status === 'uploaded' && (
                            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          )}
                          {doc.status === 'error' && (
                            <AlertCircle className="h-4 w-4 text-red-400" />
                          )}
                          {doc.status === 'pending' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeDocument(index)}
                              className="text-slate-500 hover:text-white"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-4">
                  {documents.some(d => d.status === 'pending') && (
                    <Button
                      data-testid="upload-all-btn"
                      onClick={uploadAllDocuments}
                      disabled={uploadingDoc}
                      className="btn-secondary flex-1"
                    >
                      {uploadingDoc ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Upload All Documents
                        </>
                      )}
                    </Button>
                  )}
                  
                  <Button
                    data-testid="proceed-analysis-btn"
                    onClick={proceedToAnalysis}
                    disabled={documents.some(d => d.status === 'uploading')}
                    className="btn-primary flex-1"
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    {documents.every(d => d.status === 'uploaded') ? (
                      'Proceed to Analysis'
                    ) : (
                      'Skip & View Property'
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* OCR Results Preview */}
            {documents.some(d => d.status === 'uploaded' && d.ocrText) && (
              <div className="glass-card-green">
                <h2 className="text-lg font-semibold text-white mb-4">OCR Extraction Preview</h2>
                {documents.filter(d => d.status === 'uploaded').map((doc, index) => (
                  <div key={index} className="mb-4 last:mb-0">
                    <p className="text-sm font-medium text-emerald-400 mb-2">{doc.name}</p>
                    <div className="bg-slate-900/50 p-3 rounded-lg text-xs font-mono text-slate-400 max-h-40 overflow-auto">
                      {doc.ocrText?.substring(0, 500)}
                      {doc.ocrText?.length > 500 && '...'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default UploadProperty;
