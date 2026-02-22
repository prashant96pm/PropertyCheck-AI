import React, { useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  Shield, 
  Upload, 
  FileText, 
  Loader2, 
  CheckCircle2, 
  ArrowLeft,
  X,
  AlertCircle
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
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [propertyId, setPropertyId] = useState(null);
  
  // Property form state
  const [propertyForm, setPropertyForm] = useState({
    survey_no: '',
    khata_no: '',
    state: '',
    district: '',
    taluk: '',
    village: '',
    address: ''
  });
  
  // Document upload state
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
    maxSize: 20 * 1024 * 1024 // 20MB
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
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/dashboard" className="flex items-center gap-2">
              <ArrowLeft className="h-5 w-5 text-muted-foreground" />
              <Shield className="h-8 w-8 text-primary" />
              <span className="text-xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center">
            <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
              step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-slate-200 text-slate-500'
            }`}>
              1
            </div>
            <div className={`w-24 h-1 ${step >= 2 ? 'bg-primary' : 'bg-slate-200'}`} />
            <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
              step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-slate-200 text-slate-500'
            }`}>
              2
            </div>
          </div>
        </div>

        {/* Step 1: Property Details */}
        {step === 1 && (
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="text-2xl" style={{ fontFamily: 'Playfair Display' }}>
                Property Details
              </CardTitle>
              <CardDescription>
                Enter the basic details of the property you want to verify
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePropertySubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="survey_no">Survey Number *</Label>
                    <Input
                      id="survey_no"
                      data-testid="survey-no-input"
                      value={propertyForm.survey_no}
                      onChange={(e) => setPropertyForm(prev => ({ ...prev, survey_no: e.target.value }))}
                      placeholder="e.g., 123/4"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="khata_no">Khata Number</Label>
                    <Input
                      id="khata_no"
                      data-testid="khata-no-input"
                      value={propertyForm.khata_no}
                      onChange={(e) => setPropertyForm(prev => ({ ...prev, khata_no: e.target.value }))}
                      placeholder="e.g., KH-123"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="state">State *</Label>
                    <Select 
                      value={propertyForm.state}
                      onValueChange={(value) => setPropertyForm(prev => ({ ...prev, state: value }))}
                    >
                      <SelectTrigger data-testid="state-select">
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        {INDIAN_STATES.map(state => (
                          <SelectItem key={state} value={state}>{state}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="district">District *</Label>
                    <Input
                      id="district"
                      data-testid="district-input"
                      value={propertyForm.district}
                      onChange={(e) => setPropertyForm(prev => ({ ...prev, district: e.target.value }))}
                      placeholder="e.g., Bangalore Urban"
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="taluk">Taluk</Label>
                    <Input
                      id="taluk"
                      data-testid="taluk-input"
                      value={propertyForm.taluk}
                      onChange={(e) => setPropertyForm(prev => ({ ...prev, taluk: e.target.value }))}
                      placeholder="e.g., Anekal"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="village">Village</Label>
                    <Input
                      id="village"
                      data-testid="village-input"
                      value={propertyForm.village}
                      onChange={(e) => setPropertyForm(prev => ({ ...prev, village: e.target.value }))}
                      placeholder="e.g., Sarjapur"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Full Address</Label>
                  <Input
                    id="address"
                    data-testid="address-input"
                    value={propertyForm.address}
                    onChange={(e) => setPropertyForm(prev => ({ ...prev, address: e.target.value }))}
                    placeholder="Complete property address"
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
            </CardContent>
          </Card>
        )}

        {/* Step 2: Document Upload */}
        {step === 2 && (
          <div className="space-y-6">
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="text-2xl" style={{ fontFamily: 'Playfair Display' }}>
                  Upload Documents
                </CardTitle>
                <CardDescription>
                  Upload property documents for AI-powered OCR and analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Document Type Selection */}
                <div className="space-y-2">
                  <Label>Document Type</Label>
                  <Select value={currentDocType} onValueChange={setCurrentDocType}>
                    <SelectTrigger data-testid="doc-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {DOC_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
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
                  className={`border-2 border-dashed rounded-sm p-8 text-center cursor-pointer transition-colors ${
                    isDragActive ? 'border-accent bg-accent/5' : 'border-slate-300 hover:border-accent'
                  }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  {isDragActive ? (
                    <p className="text-accent">Drop files here...</p>
                  ) : (
                    <>
                      <p className="text-muted-foreground mb-2">
                        Drag & drop documents here, or click to browse
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Supports PDF, PNG, JPG, TIFF (max 20MB)
                      </p>
                    </>
                  )}
                </div>

                {/* Document List */}
                {documents.length > 0 && (
                  <div className="space-y-3">
                    <Label>Queued Documents</Label>
                    {documents.map((doc, index) => (
                      <div 
                        key={index}
                        className="flex items-center justify-between p-3 border rounded-sm"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm font-medium">{doc.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {DOC_TYPES.find(t => t.value === doc.type)?.label}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {doc.status === 'pending' && (
                            <span className="text-xs text-muted-foreground">Pending</span>
                          )}
                          {doc.status === 'uploading' && (
                            <Loader2 className="h-4 w-4 animate-spin text-accent" />
                          )}
                          {doc.status === 'uploaded' && (
                            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                          )}
                          {doc.status === 'error' && (
                            <AlertCircle className="h-4 w-4 text-red-600" />
                          )}
                          {doc.status === 'pending' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeDocument(index)}
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
                    disabled={documents.length === 0 || documents.some(d => d.status === 'uploading')}
                    className="btn-primary flex-1"
                  >
                    {documents.every(d => d.status === 'uploaded') ? (
                      'Proceed to Analysis'
                    ) : (
                      'Skip & View Property'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* OCR Results Preview */}
            {documents.some(d => d.status === 'uploaded' && d.ocrText) && (
              <Card className="card-base">
                <CardHeader>
                  <CardTitle className="text-lg">OCR Extraction Preview</CardTitle>
                </CardHeader>
                <CardContent>
                  {documents.filter(d => d.status === 'uploaded').map((doc, index) => (
                    <div key={index} className="mb-4 last:mb-0">
                      <p className="text-sm font-medium mb-2">{doc.name}</p>
                      <div className="bg-slate-100 p-3 rounded-sm text-xs font-mono max-h-40 overflow-auto">
                        {doc.ocrText?.substring(0, 500)}
                        {doc.ocrText?.length > 500 && '...'}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default UploadProperty;
