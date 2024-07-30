from sklearn.metrics import pairwise_distances
from app import app, db
from models import Opportunity, OptimizedOpportunity
import numpy as np
from sentence_transformers import SentenceTransformer

def ranker(query, vector):
    """
    This function performs a similarity search on the embeddings in the database and returns the 25 most similar opportunities.
    
    Args:
        vector (numpy array): The vector to compare against the embeddings in the database.
        
    Returns:
        list: A list of the 25 most similar opportunities.
    """
    print("Ranker function called")
    with app.app_context():
        # Fetch all opportunities at once
        print("Fetching opportunities...")
        # opportunities = Opportunity.query.all()
        # embedding_vectors = Opportunity.query.options(load_only(Opportunity.embedding_vector)).all()
        embedding_vectors = db.session.query(OptimizedOpportunity.embedding_vector).all()
        embedding_vectors = [item[0] for item in embedding_vectors]  # Unpack the tuples
        print("Opportunities fetched")
        
        # Ensure the input vector is a numpy array
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector)
            print("Had to change it")
        print("Vector is a numpy array")

        # Get the list of all embedding vectors
        list_of_vectors = np.array(embedding_vectors)
        print("List of vectors created")

        # Compute the cosine distances
        distances = pairwise_distances(vector.reshape(1, -1), list_of_vectors, metric='cosine')[0]
        print("Distances computed")

        # Sort the distances and get the minimum 10
        min_4_distances = np.sort(distances)[:4]

        # Indices of the minimum 10 distances
        min_4_indices = np.argsort(distances)[:4]

        # Fetch the opportunities from the results
        top_opportunities = []


        # Fetch the opportunities from the results
        for index in min_4_indices:
            opportunity = OptimizedOpportunity.query.filter_by(embedding_vector=embedding_vectors[index]).first()
            top_opportunities.append(opportunity)

        output_string = "The user's query: " + query + "\n\n"
        choices = ["one", "another", "yet another", "another"]
        i = 0
        for opp in top_opportunities:
            page_contents = opp.long_text
            intro = ("Here are the details of " + choices[i] + " relevant opportunity:\n")
            output_string += intro 
            output_string += page_contents + "\n"
            i += 1            
 
        return (output_string)


        # # Calculate cosine similarity with each opportunity's embedding_vector
        # for opportunity in opportunities:
        #     if opportunity.embedding_vector:
        #         opp_vector = np.array(opportunity.embedding_vector)
        #         if vector.shape[0] == opp_vector.shape[0]:  # Ensure dimensions match
        #             similarity = cosine_similarity([vector], [opp_vector])[0][0]
        #             top_opportunities.append((opportunity, similarity))

    # # Sort by similarity (descending)
    # top_opportunities.sort(key=lambda x: x[1], reverse=True)

    # # Return top 25 similar opportunities
    # return top_opportunities[:25]

if __name__ == "__main__":
    import cProfile

    # vector = np.array([-0.05899234488606453, 0.023830251768231392, 0.08223085105419159, 0.07898467034101486, 0.022901667281985283, -0.06488318741321564, -0.00631936127319932, 0.013512449339032173, 0.02367941476404667, -0.06936285644769669, -0.05079726502299309, -0.06880652904510498, -0.016151880845427513, -0.06635811924934387, 0.035653624683618546, 0.02662229724228382, 0.032179780304431915, -0.047055818140506744, -0.06359728425741196, 0.04372672364115715, 0.03257187828421593, 0.03176043555140495, -0.03698912635445595, -0.0783592239022255, -0.036877091974020004, -0.022199813276529312, -0.039418935775756836, 0.008427527733147144, 0.014519121497869492, 0.04711121320724487, 0.05976489558815956, 0.11334840953350067, 0.013904237188398838, -0.00029091612668707967, 0.06407615542411804, 0.04532434418797493, -0.037705134600400925, 0.017521023750305176, -0.02848762832581997, 0.05681409686803818, -0.05598359555006027, -0.11359812319278717, 0.04122092202305794, 0.012503212317824364, -0.019303414970636368, -0.04407087713479996, -0.029243262484669685, -0.06511635333299637, 0.0018448123009875417, -0.006888717878609896, 0.03933396190404892, 0.039703916758298874, -0.03171193227171898, 0.07417063415050507, -0.02752608060836792, 0.05060680955648422, -0.05856303870677948, -0.07040493190288544, 0.006550101563334465, -0.016770705580711365, -0.01453704759478569, -0.05037436634302139, -0.0772588923573494, -0.05219237506389618, 0.06645307689905167, -0.0024122707545757294, -0.021993715316057205, 0.016716955229640007, -0.018925314769148827, -0.08572464436292648, -0.01477824430912733, 0.0438997745513916, -0.1027948334813118, -0.010979737155139446, 0.034460581839084625, 0.0998409241437912, 0.07327910512685776, 0.0787423849105835, 0.11409693956375122, -0.08535169810056686, 0.06996958702802658, 0.02770613133907318, -0.06565017998218536, -0.055832043290138245, -0.031097887083888054, 0.04578939452767372, 0.00928586721420288, 0.1647343933582306, 0.07062279433012009, 0.06875548511743546, -0.04095990210771561, -0.03040364198386669, -0.016625508666038513, -0.02053663693368435, 0.03689529374241829, 0.10792625695466995, 0.017209341749548912, -0.12405905872583389, 0.06725865602493286, 0.046723417937755585, 0.025533054023981094, 0.001248453976586461, -0.11174234747886658, 0.00987768080085516, -0.07413236051797867, 0.028851594775915146, 0.0005843678954988718, 0.04350638762116432, -0.010038863867521286, -0.019235482439398766, 0.02982085943222046, -0.020916348323225975, 0.01386881060898304, -0.09160392731428146, 0.003990186844021082, 0.008591518737375736, -0.05077045038342476, 0.0641096904873848, -0.02586209587752819, -0.056607771664857864, -0.06551232188940048, 0.03909721598029137, 0.04465105012059212, 0.052134957164525986, -0.05161958932876587, -0.07242827862501144, 0.012520610354840755, 4.048891109071519e-33, 0.0425223670899868, -0.02912932261824608, 0.01929299905896187, 0.05529554560780525, -0.0442575179040432, 0.0886814296245575, -0.039019156247377396, 0.041939131915569305, -0.05115609988570213, -0.06386709958314896, -0.039719108492136, 0.030588384717702866, 0.040388189256191254, 0.01757276989519596, 0.024576621130108833, -0.06222395598888397, 0.06887760013341904, 0.029923737049102783, 0.0181028600782156, 0.006851537618786097, 0.012085121124982834, 0.005808735266327858, 0.01714855432510376, 0.013269202783703804, 0.08165688812732697, 0.06804034858942032, -0.02302188239991665, -0.09435594081878662, 0.00594788882881403, 0.005910767707973719, 0.010373476892709732, -0.034048207104206085, -0.039807140827178955, 0.0006455603870563209, -0.014554823748767376, 0.055325962603092194, -0.011953093111515045, 0.018577491864562035, -0.03774529695510864, -0.06528256833553314, -0.06811785697937012, 0.09367793798446655, -0.04365198314189911, 0.04675201326608658, 0.00550776207819581, -0.006175122689455748, 0.15522755682468414, -0.011381668969988823, 0.04727453365921974, 0.050172463059425354, -0.021890897303819656, 0.020151479169726372, -0.06624308228492737, -0.03577427566051483, 0.022646650671958923, -0.0368463471531868, -0.006637421902269125, -0.012868614867329597, -0.0037762336432933807, 0.03801655024290085, 0.041237398982048035, 0.02457689680159092, -0.04254574328660965, -0.05407577008008957, 0.012305205687880516, 0.11061659455299377, 0.004722448065876961, 0.026016652584075928, 0.0007272383663803339, 0.014559753239154816, 0.020140711218118668, -0.07038944959640503, 0.023999148979783058, 0.05909718945622444, 0.04003644362092018, 0.003755429293960333, 0.045904599130153656, -0.007345808669924736, -0.024085992947220802, 0.04722169414162636, -0.05984422564506531, 0.002475999528542161, 0.012179582379758358, -0.07805681228637695, -0.056430596858263016, -0.02421889454126358, -0.015888359397649765, 0.010723095387220383, -0.00408146670088172, -0.029122458770871162, 0.044551052153110504, -0.008966466411948204, 0.03765077143907547, 0.0708647146821022, -0.006983030587434769, -5.365479679481021e-33, -0.013668220490217209, -0.01652560383081436, -0.07966563105583191, -0.08659776300191879, 0.05216803774237633, 0.04626493901014328, -0.00023626151960343122, 0.020408574491739273, -0.06416976451873779, -0.017175495624542236, -0.048497699201107025, 0.04522846266627312, 0.019479338079690933, -0.08172906935214996, -0.041483961045742035, -0.07397717237472534, -0.08511115610599518, 0.09679584205150604, -0.02535848692059517, 0.08066681772470474, -0.0028596126940101385, 0.10300461947917938, -0.005564082879573107, -0.006555321626365185, 0.052001431584358215, 0.038029491901397705, 0.03290887549519539, -0.043320879340171814, -0.018622856587171555, 0.05936747044324875, -0.06460131704807281, 0.04497016593813896, -0.10752622038125992, 0.05655388906598091, 0.03270404413342476, 0.0194048210978508, 0.05970955267548561, -0.08162263035774231, -0.06989775598049164, -0.01752130687236786, -0.030080610886216164, 0.033051978796720505, 0.007415023632347584, -0.007409194950014353, -0.04478969797492027, 0.036147590726614, -0.05878105014562607, 0.1257253885269165, 0.04539463296532631, 0.0005382902454584837, 0.008307811804115772, -0.037247367203235626, -0.04499507695436478, 0.062193892896175385, 0.07828152179718018, 0.003320148680359125, 0.07622051239013672, 0.010062958113849163, -0.02279391512274742, 0.004296016413718462, 0.07539437711238861, 0.010500235483050346, 0.06107054650783539, 0.020388303324580193, 0.014408137649297714, -0.05768167972564697, 0.026135291904211044, 0.047191862016916275, -0.054863374680280685, -0.06257394701242447, 0.09724333137273788, -0.08823169022798538, -0.021027030423283577, -0.025725873187184334, 0.052068427205085754, 0.03622540831565857, 0.12835907936096191, -0.02304084040224552, -0.02604341134428978, 0.02445574291050434, -0.07384933531284332, 0.07231984287500381, 0.032890867441892624, -0.005249231122434139, 0.006239231210201979, -0.06676200777292252, -0.0061262669041752815, -0.07153636962175369, -0.048821158707141876, 0.08275381475687027, -0.08273669332265854, -0.007223788648843765, 0.004429698921740055, 0.12953752279281616, -0.012080451473593712, -5.806789360462972e-08, 0.01937396451830864, 0.01207821536809206, 0.03154738247394562, -0.01602541096508503, -0.039917733520269394, -0.0028235726058483124, -0.02003720961511135, -0.01498115248978138, 0.06115105748176575, -0.004542682785540819, 0.05170218273997307, -0.033299125730991364, 0.01876990683376789, -0.05039287731051445, -0.035274021327495575, -0.03684968873858452, 0.011564075946807861, -0.026764772832393646, -0.02622826211154461, 0.013447161763906479, 0.025170210748910904, -0.03550586476922035, 0.023622212931513786, -0.07614187896251678, 0.03996032476425171, -0.046528298407793045, 0.01711956411600113, 0.046447671949863434, -0.0323997400701046, -0.0779358521103859, -0.004376315511763096, -0.03137274459004402, 0.011356902308762074, -0.056246090680360794, -0.042915284633636475, 0.0839415118098259, -0.08165596425533295, 0.012494181282818317, 0.03341033682227135, 0.05725161358714104, 0.0025519574992358685, -0.0058610765263438225, 0.029549187049269676, 0.003927556797862053, -0.013792104087769985, 0.028491906821727753, -0.10371313989162445, -0.09471485018730164, 0.009044226258993149, 0.051465343683958054, -0.05512073636054993, -0.06796136498451233, 0.028925210237503052, -0.0742657333612442, -0.04998847842216492, 0.056750815361738205, -0.13722561299800873, 0.019882120192050934, 0.03339969739317894, 0.009394603781402111, 0.061559904366731644, -0.023979999125003815, -0.09814368188381195, -0.003601970849558711])  # Example vector

    # Profile the ranker function
    profiler = cProfile.Profile()
    profiler.enable()

    # Example usage
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query = "I have a nonprofit that uses peer-led strategies to improve people’s mental health. We create an environment that allows people to engage and form meaningful relationships with others like them. We specifically serve the LGBTQIA+ community, independent artists, and mothers. We do not perform any research or trials. We rely on trained, but not certified paraprofessionals to lead these meetings as a mentor. What funding opportunity should I apply to?"
    vector = model.encode(query)

    output = ranker("I have a nonprofit that uses peer-led strategies to improve people’s mental health. We create an environment that allows people to engage and form meaningful relationships with others like them. We specifically serve the LGBTQIA+ community, independent artists, and mothers. We do not perform any research or trials. We rely on trained, but not certified paraprofessionals to lead these meetings as a mentor. What funding opportunity should I apply to?", vector)

    print(output)

    profiler.disable()
    profiler.dump_stats('profile_data.prof')

